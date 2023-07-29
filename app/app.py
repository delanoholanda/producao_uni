### versão finalizada

import tempfile
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
# import pandas as pd

from functions.process_pdf import extrairTextoPdf,  tratarTextoExtraido
from functions.data_filters import buscaLotesCodigos, filtroAllCodigo, filtroByCodigo, filtroByCodigo2, filtroByAT, obter_beneficiarios_desejados, obter_beneficiarios_AT
from functions.create_dataframe import montarDataFrame


app = Flask(__name__)


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




if __name__ == '__main__':
    app.run(debug=True)




