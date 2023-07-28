### versão finalizada

import tempfile
import os
from flask import Flask, render_template, request, jsonify
import pandas as pd

from functions.process_pdf import extrairTextoPdf,  tratarTextoExtraido, format_brazilian_currency
from functions.data_filters import buscaLotesCodigos, filtroAllCodigo, filtroByCodigo, filtroByCodigo2, filtroByAT
from functions.create_dataframe import montarDataFrame


app = Flask(__name__)


DATAFRAME_ORIGINAL = None
DATAFRAME_INDEX = None


@app.route('/', methods=['GET', 'POST'])
def index():
    global DATAFRAME_ORIGINAL
    global DATAFRAME_INDEX
    
    atualizar_param = request.args.get('atualizar')

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            # Create a temporary file to store the uploaded PDF data
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name
                file.save(temp_file_path)

            texto_extraido = extrairTextoPdf(temp_file_path)
            lista_diferentes_lotes, lista_diferentes_codigos = buscaLotesCodigos(texto_extraido)
            texto_processado = tratarTextoExtraido(texto_extraido, lista_diferentes_lotes, lista_diferentes_codigos)
            df = montarDataFrame(lista_diferentes_codigos, texto_processado)
            
            DATAFRAME_ORIGINAL = df

            # Remove the temporary file after processing
            os.remove(temp_file_path)

            # df_exibir = filtroAllCodigo(df, lista_diferentes_codigos)

            df_exibir = filtroByCodigo2(df,codigo="5000510")

            DATAFRAME_INDEX = df_exibir

            
            return render_template('dados_producao.html', table=df_exibir.to_html(classes='table table-bordered table-striped', index=False))
    
    if DATAFRAME_INDEX is None or atualizar_param == 'True':
        # return "No dataframe available."
        return render_template('index.html')
    else:
        return render_template('dados_producao.html', table=DATAFRAME_INDEX.to_html(classes='table table-bordered table-striped', index=False))



@app.route('/filtro-elizza', methods=['GET'])
def filtro_elizza():
    global DATAFRAME_ORIGINAL
    if DATAFRAME_ORIGINAL is None:
        return "No dataframe available."
    # print(DATAFRAME_ORIGINAL)
    # Fazendo o filtro com base nos beneficiários desejados
    beneficiarios_desejados = ["ARTHUR MIGUEL C QUEIROZ", "CAIO ALMEIDA CARNEIRO", "CECILIA PEREIRA MACHADO",
                                 "ERIC ALMEIDA CARNEIRO", "JOAO GUILHERME S SANTOS", "JOAO LUCAS D QUEIROZ", 
                                 "JOAO MIGUEL PARENTE GOMES", "LUIZ GABRIEL O ALVES", "YAN LUCCA LEMOS GOMES"]
    
    codigo = "5000510"
    df_exibir = filtroByAT(DATAFRAME_ORIGINAL, beneficiarios_desejados, codigo)
    # df_html = df_exibir.to_html(classes='table table-bordered table-striped', index=False)
    # return render_template('filtro_codigo.html', df_html=df_html)
    return render_template('filtro_AT.html', table=df_exibir.to_html(classes='table table-bordered table-striped', index=False), AT="Produção da Elizza")
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




