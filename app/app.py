### versão finalizada

import tempfile
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Profissional, Beneficiario, Producao, DadosProducao
from functions.dao import criar_beneficiarios_do_dataframe, criar_nova_producao, adicionar_profissionais
import locale


from functions.process_pdf import extrairTextoPdf,  tratarTextoExtraido
from functions.data_filters import buscaLotesCodigos, filtroAllCodigo, filtroByCodigo, filtroByCodigo2, filtroByAT, obter_beneficiarios_desejados, obter_beneficiarios_AT, filtroByAtBd
from functions.create_dataframe import montarDataFrame


app = Flask(__name__)

# Especifica o caminho completo para a pasta "data" no diretório do projeto
data_folder = os.path.join(os.path.dirname(__file__), 'data')

# Garante que a pasta "data" exista, caso contrário, cria-a
os.makedirs(data_folder, exist_ok=True)

# Especifica o caminho completo para o arquivo do banco de dados dentro da pasta "data"
db_path = os.path.join(data_folder, 'database.db')


app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'  # Usando banco de dados SQLite


# Inicializa o objeto 'db' com o aplicativo Flask
db.init_app(app)

# Cria o banco de dados
with app.app_context():
    db.create_all()
    adicionar_profissionais()


DATAFRAME_ORIGINAL = None
DATAFRAME_INDEX = None


@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = request.args.get('error_message', default=None)
    global DATAFRAME_ORIGINAL
    global DATAFRAME_INDEX
    global PRODUCAO

    
    atualizar_param = request.args.get('atualizar')

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            # Create a temporary file to store the uploaded PDF data
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name
                file.save(temp_file_path)

            texto_extraido, linha_producao_movimento  = extrairTextoPdf(temp_file_path)
            
            # Verifica se o PDF é o correto
            if linha_producao_movimento:
                lista_diferentes_lotes, lista_diferentes_codigos = buscaLotesCodigos(texto_extraido)
                texto_processado = tratarTextoExtraido(texto_extraido, lista_diferentes_lotes, lista_diferentes_codigos)
                df = montarDataFrame(lista_diferentes_codigos, texto_processado)
            

                PRODUCAO = linha_producao_movimento.group()

                producao_movimetacao = PRODUCAO
                # Verificar se a produção já existe com o mesmo valor em producao_movimetacao
                producao_existente = Producao.query.filter_by(producao_movimetacao=producao_movimetacao).first()

                beneficiarios_AT = obter_beneficiarios_AT()

                criar_beneficiarios_do_dataframe(df, beneficiarios_AT)

                if producao_existente is None:
                    criar_nova_producao(df, producao_movimetacao)

                            

                DATAFRAME_ORIGINAL = df

                # Remove the temporary file after processing
                os.remove(temp_file_path)

                # df_exibir = filtroAllCodigo(df, lista_diferentes_codigos)

                # beneficiarios_AT = obter_beneficiarios_AT()

                codigo = "5000510"
                df_exibir = filtroByCodigo2(df, codigo, beneficiarios_AT)

                DATAFRAME_INDEX = df_exibir
                # DATAFRAME_INDEX = df
                    

                    # return render_template('dados_producao.html', table=DATAFRAME_INDEX.to_html(classes='table table-bordered table-striped', index=False))
                return render_template('dados_producao.html', table=df_exibir.to_html(classes='table table-bordered table-striped', index=False), producao=PRODUCAO)
            else:
                error_message = "PDF Inválido!"
                return render_template('index.html', error_message=error_message)
    
    if DATAFRAME_INDEX is None or atualizar_param == 'True':
        # return "No dataframe available."
        return render_template('index.html', error_message=error_message)
    else:
        return render_template('dados_producao.html', table=DATAFRAME_INDEX.to_html(classes='table table-bordered table-striped', index=False), producao=PRODUCAO)



@app.route('/filtro-at', methods=['GET'])
def filtro_at():

    profissional = request.args.get('at')

    global DATAFRAME_ORIGINAL
    if DATAFRAME_ORIGINAL is None:
        error_message = "Necessário adicionar um PDF"
        return redirect(url_for('index',error_message=error_message), code=302) 
    
    beneficiarios_desejados = obter_beneficiarios_desejados(profissional)
    beneficiarios_AT = obter_beneficiarios_AT()

    codigo = "5000510"
    df_exibir = filtroByAT(DATAFRAME_ORIGINAL, beneficiarios_desejados, beneficiarios_AT, codigo, profissional)

    # Verificar se o DataFrame filtrado está vazio
    if df_exibir.empty:
        return render_template('filtro_AT.html', semDados="Você não possui nenhum atendimento na produção: " + PRODUCAO, AT="Produção da " + profissional, producao=PRODUCAO)
    else:
        # df_html = df_exibir.to_html(classes='table table-bordered table-striped', index=False)
        # return render_template('filtro_codigo.html', df_html=df_html)
        return render_template('filtro_AT.html', table=df_exibir.to_html(classes='table table-bordered table-striped', index=False), AT="Produção da " + profissional, producao=PRODUCAO)
        # return jsonify({'html': df_html})


@app.route('/producao_data_hora', methods=['GET'])
def producao_data_hora():


    global DATAFRAME_ORIGINAL
    if DATAFRAME_ORIGINAL is None:
        error_message = "Necessário adicionar um PDF"
        return redirect(url_for('index',error_message=error_message), code=302)


    df_exibir = DATAFRAME_ORIGINAL

    # Remover a coluna 'Lote'
    df_exibir = df_exibir.drop('Lote', axis=1)

     # Selecione apenas as linhas com o código "5000510"
    df_codigo = df_exibir[df_exibir['Código'] == "5000510"]

    # return render_template('producao_data_hora.html', df_exibir=df_exibir, producao=PRODUCAO)
    return render_template('producao_data_hora.html', table=df_codigo.to_html(classes='table table-bordered table-striped', index=False), producao=PRODUCAO)

    # return jsonify({'html': df_html})


@app.route('/all_dados', methods=['GET'])
def all_dados():
    global DATAFRAME_INDEX
    if DATAFRAME_INDEX is None:
        return "No dataframe available."
    # print(DATAFRAME_ORIGINAL)
    # Fazendo o filtro com base nos beneficiários desejados
    
    # df_html = DATAFRAME_INDEX.to_html(classes='table table-bordered table-striped', index=False)
    # return render_template('filtro_codigo.html', df_html=df_html)
    return render_template('result.html', table=DATAFRAME_INDEX.to_html(classes='table table-bordered table-striped'))


# Rotas para CRUD de Profissional
@app.route('/profissional', methods=['GET', 'POST'])
def profissional():
    if request.method == 'POST':
        nome = request.form['nome']
        novo_profissional = Profissional(nome=nome)
        db.session.add(novo_profissional)
        db.session.commit()
    profissionais = Profissional.query.all()
    return render_template('profissional.html', profissionais=profissionais)

@app.route('/profissional/delete/<int:id>')
def delete_profissional(id):
    profissional = Profissional.query.get_or_404(id)
    db.session.delete(profissional)
    db.session.commit()
    return redirect(url_for('profissional'))


# Rota para renderizar o formulário de edição do Profissional
@app.route('/profissional/edit/<int:id>', methods=['GET'])
def edit_profissional(id):
    profissional = Profissional.query.get_or_404(id)
    return render_template('edit_profissional.html', profissional=profissional)

# Rota para processar a submissão do formulário de edição do Profissional
@app.route('/profissional/edit/<int:id>', methods=['POST'])
def update_profissional(id):
    profissional = Profissional.query.get_or_404(id)
    profissional.nome = request.form['nome']
    db.session.commit()
    return redirect(url_for('profissional'))



# Rotas para CRUD de Beneficiario
@app.route('/beneficiario', methods=['GET', 'POST'])
def beneficiario():
    if request.method == 'POST':
        nome = request.form['nome']
        profissional_id = request.form['profissional_id']
        novo_beneficiario = Beneficiario(nome=nome, profissional_id=profissional_id)
        db.session.add(novo_beneficiario)
        db.session.commit()
    beneficiarios = Beneficiario.query.all()
    profissionais = Profissional.query.all()

    # Consulta todos os beneficiários e ordena pelo campo 'nome' em ordem crescente
    beneficiarios = Beneficiario.query.order_by(Beneficiario.nome).all()
    
    return render_template('beneficiario.html', beneficiarios=beneficiarios, profissionais=profissionais)

@app.route('/beneficiario/delete/<int:id>')
def delete_beneficiario(id):
    beneficiario = Beneficiario.query.get_or_404(id)
    db.session.delete(beneficiario)
    db.session.commit()
    return redirect(url_for('beneficiario'))


# Rota para renderizar o formulário de edição do Beneficiario
@app.route('/beneficiario/edit/<int:id>', methods=['GET'])
def edit_beneficiario(id):
    beneficiario = Beneficiario.query.get_or_404(id)
    profissionais = Profissional.query.all()
    return render_template('edit_beneficiario.html', beneficiario=beneficiario, profissionais=profissionais)

# Rota para processar a submissão do formulário de edição do Beneficiario
# @app.route('/beneficiario/edit/<int:id>', methods=['POST'])
# def update_beneficiario(id):
#     beneficiario = Beneficiario.query.get_or_404(id)
#     beneficiario.nome = request.form['nome']
#     beneficiario.profissional_id = request.form['profissional_id']
#     db.session.commit()
#     return redirect(url_for('beneficiario'))


@app.route('/beneficiario/edit/<int:id>', methods=['POST'])
def update_beneficiario(id):
    beneficiario = Beneficiario.query.get_or_404(id)
    beneficiario.nome = request.form['nome']
    beneficiario.tipo = request.form['tipo']  # Atualize o campo 'tipo'
    
    # Obtenha os IDs dos novos atendentes do formulário
    atendente_1_id = int(request.form['atendente_1']) if request.form['atendente_1'] else None
    atendente_2_id = int(request.form['atendente_2']) if request.form['atendente_2'] else None
    atendente_3_id = int(request.form['atendente_3']) if request.form['atendente_3'] else None

    # Obtenha os objetos Profissional correspondentes aos atendentes do formulário
    atendente_1 = Profissional.query.get(atendente_1_id) if atendente_1_id else None
    atendente_2 = Profissional.query.get(atendente_2_id) if atendente_2_id else None
    atendente_3 = Profissional.query.get(atendente_3_id) if atendente_3_id else None

    # Atribua os atendentes ao Beneficiario
    beneficiario.atendente_1 = atendente_1
    beneficiario.atendente_2 = atendente_2
    beneficiario.atendente_3 = atendente_3

    db.session.commit()
    return redirect(url_for('beneficiario'))


# Route to display the existing productions in the HTML template
@app.route('/show_producoes')
def show_producoes():
    producoes = Producao.query.all()
    return render_template('show_producoes.html', producoes=producoes)


# Route to display the data for a specific production
@app.route('/todos_dados_producao/<int:producao_id>')
def todos_dados_producao(producao_id):
    # Definir a localização para o Brasil (outra opção seria 'pt_BR.utf8')
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
    
    producao = Producao.query.get(producao_id)
    if producao is None:
        return "Production not found."
    else:
        # Format the data_hora values in the producao object
        for dado in producao.dados_producao:
            dado.formatted_data_hora = dado.data_hora.strftime('%H:%M:%S - %d/%m/%Y')

        # Obter os nomes dos beneficiários correspondentes aos IDs
        nomes_beneficiarios = {}
        for dado in producao.dados_producao:
            beneficiario_id = dado.beneficiario_id
            beneficiario_nome = Beneficiario.query.get(beneficiario_id).nome
            nomes_beneficiarios[beneficiario_id] = beneficiario_nome
        
       
        # Formatar os valores monetários
        for dado in producao.dados_producao:
             dado.formatted_valor = locale.currency(dado.valor, grouping=True)


        return render_template('todos_dados_producao.html', producao=producao, nomes_beneficiarios=nomes_beneficiarios)

@app.route('/filtro-at-bd', methods=['GET'])
def filtro_at_bd():

    # Defina a localização para o Brasil
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    
    profissional = request.args.get('at')

    producao_id = request.args.get('producao')

    # Use a função query.get() para buscar a produção com base no ID
    producao = Producao.query.get(producao_id)


    # global DATAFRAME_ORIGINAL
    # if DATAFRAME_ORIGINAL is None:
    #     error_message = "Necessário adicionar um PDF"
    #     return redirect(url_for('index',error_message=error_message), code=302) 
    
    beneficiarios_desejados = obter_beneficiarios_desejados(profissional)
    beneficiarios_AT = obter_beneficiarios_AT()

    codigo = "5000510"

    result = filtroByAtBd(beneficiarios_AT, beneficiarios_desejados, codigo, profissional, producao)

    # Suponha que 'result' é uma lista de dicionários com seus dados
    for dado in result:
        # Formate o valor 'Valor/Atendimento' como moeda brasileira
        dado['Valor/Atendimento'] = locale.currency(dado['Valor/Atendimento'], grouping=True, symbol=None)
        dado['Recebido'] = locale.currency(dado['Recebido'], grouping=True, symbol=None)
        dado['Devido'] = locale.currency(dado['Devido'], grouping=True, symbol=None)
        dado['Saldo Mãe'] = locale.currency(dado['Saldo Mãe'], grouping=True, symbol=None)
        dado['Parceiro - 60%'] = locale.currency(dado['Parceiro - 60%'], grouping=True, symbol=None)
        dado['Parceiro - 40%'] = locale.currency(dado['Parceiro - 40%'], grouping=True, symbol=None)
        dado['Imposto Retido'] = locale.currency(dado['Imposto Retido'], grouping=True, symbol=None)

        


    return render_template('filtro_AT_DB.html', dados=result, producao=producao, AT="Produção da " + profissional)

    # # Verificar se o DataFrame filtrado está vazio
    # if result.empty:
    #     return render_template('filtro_AT_DB.html', semDados="Você não possui nenhum atendimento na produção: " + PRODUCAO, AT="Produção da " + profissional, producao=PRODUCAO)
    # else:
    #     # df_html = df_exibir.to_html(classes='table table-bordered table-striped', index=False)
    #     # return render_template('filtro_codigo.html', df_html=df_html)
    #     return render_template('filtro_AT_DB.html', table=result.to_html(classes='table table-bordered table-striped', index=False), AT="Produção da " + profissional, producao=PRODUCAO)
    #     # return jsonify({'html': df_html})


# # Rotas para CRUD de Producao
# @app.route('/beneficiario', methods=['GET', 'POST'])
# def beneficiario():
#     if request.method == 'POST':
#         nome = request.form['nome']
#         profissional_id = request.form['profissional_id']
#         novo_beneficiario = Beneficiario(nome=nome, profissional_id=profissional_id)
#         db.session.add(novo_beneficiario)
#         db.session.commit()
#     beneficiarios = Beneficiario.query.all()
#     profissionais = Profissional.query.all()
#     return render_template('beneficiario.html', beneficiarios=beneficiarios, profissionais=profissionais)

# @app.route('/beneficiario/delete/<int:id>')
# def delete_beneficiario(id):
#     beneficiario = Beneficiario.query.get_or_404(id)
#     db.session.delete(beneficiario)
#     db.session.commit()
#     return redirect(url_for('beneficiario'))


if __name__ == '__main__':
    app.run(debug=True)




