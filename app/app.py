### versão finalizada

import tempfile
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Profissional, Paciente
# import pandas as pd

from functions.process_pdf import extrairTextoPdf,  tratarTextoExtraido
from functions.data_filters import buscaLotesCodigos, filtroAllCodigo, filtroByCodigo, filtroByCodigo2, filtroByAT, obter_beneficiarios_desejados, obter_beneficiarios_AT
from functions.create_dataframe import montarDataFrame


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Usando banco de dados SQLite

# Inicializa o objeto 'db' com o aplicativo Flask
db.init_app(app)

# Cria o banco de dados
with app.app_context():
    db.create_all()


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
                DATAFRAME_ORIGINAL = df

                # Remove the temporary file after processing
                os.remove(temp_file_path)

                # df_exibir = filtroAllCodigo(df, lista_diferentes_codigos)

                beneficiarios_AT = obter_beneficiarios_AT()

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



# Rotas para CRUD de Paciente
@app.route('/paciente', methods=['GET', 'POST'])
def paciente():
    if request.method == 'POST':
        nome = request.form['nome']
        profissional_id = request.form['profissional_id']
        novo_paciente = Paciente(nome=nome, profissional_id=profissional_id)
        db.session.add(novo_paciente)
        db.session.commit()
    pacientes = Paciente.query.all()
    profissionais = Profissional.query.all()
    return render_template('paciente.html', pacientes=pacientes, profissionais=profissionais)

@app.route('/paciente/delete/<int:id>')
def delete_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    db.session.delete(paciente)
    db.session.commit()
    return redirect(url_for('paciente'))


# Rota para renderizar o formulário de edição do Paciente
@app.route('/paciente/edit/<int:id>', methods=['GET'])
def edit_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    profissionais = Profissional.query.all()
    return render_template('edit_paciente.html', paciente=paciente, profissionais=profissionais)

# Rota para processar a submissão do formulário de edição do Paciente
@app.route('/paciente/edit/<int:id>', methods=['POST'])
def update_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    paciente.nome = request.form['nome']
    paciente.profissional_id = request.form['profissional_id']
    db.session.commit()
    return redirect(url_for('paciente'))


if __name__ == '__main__':
    app.run(debug=True)




