### versão finalizada

import tempfile
import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
import re
import PyPDF2

app = Flask(__name__)

TEXTO_EXTRAIDO = ""
CODIGOS_DIFERENTES = ""
LOTES_DIFERENTES = ""
DATAFRAME_ORIGINAL = None
DATAFRAME_INDEX = None

def extrairTextoPdf(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as arquivo:
        leitor_pdf = PyPDF2.PdfReader(arquivo)
        num_paginas = len(leitor_pdf.pages)

        texto_completo = 'Lote Nota Data Beneficiário Total Código Qt. Cobr Qt. Paga Valor Qtd CH Subtotal\n'
        padrao_pagina = re.compile(r'Página:\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}Modelo Completo')
        padrao_texto_adicional = re.compile(r'\d+Data de Emissão:.*?SERTAO CENTRAL', re.DOTALL)
        padrao_cabecalho = re.compile(r'Lote Nota Data Beneficiário Código Qt\. Cobr Qt\. Paga Valor Qtd CH Subtotal Total Nota', re.DOTALL)

        for pagina in range(num_paginas):
            pagina_pdf = leitor_pdf.pages[pagina]
            texto = pagina_pdf.extract_text()

            # Verifica se a página contém o padrão "Página: [data e hora]"
            if padrao_pagina.search(texto):
                # Remove o texto correspondente ao padrão da página
                texto = padrao_pagina.sub('', texto)

            # Remove os textos adicionais usando a expressão regular
            texto = padrao_texto_adicional.sub('', texto)

            # Verifica se a linha está vazia e, se sim, ignora a linha
            linhas = texto.split('\n')
            for linha in linhas:
                if linha.strip() and not linha.startswith('Lote'):  # Verifica se a linha não é vazia e não começa com "Lote"
                    # Adiciona a linha ao texto completo apenas se não for o cabeçalho
                    if not padrao_cabecalho.match(linha):
                        texto_completo += linha + '\n'

        # Remove o texto "DETALHAMENTO DOS SERVIÇOS PRESTADOS" e outras substituições
        texto_completo = texto_completo.replace("DETALHAMENTO DOS SERVIÇOS PRESTADOS", "")
        texto_completo = texto_completo.replace("GlobalValor Dimensão", "")
        texto_completo = texto_completo.replace("SERVICOS DIVERSOS", "")
        texto_completo = texto_completo.replace("Dimensão\n\nIndividual", "")
        texto_completo = texto_completo.replace("Número Cartão ", "")
        texto_completo = texto_completo.replace("Filme ", "")
        texto_completo = texto_completo.replace("Mensagem  de Glosa ", "")
        texto_completo = texto_completo.replace("Valor Dimensão ", "")
        texto_completo = texto_completo.replace("Individual", "")
        texto_completo = texto_completo.replace("SubtotalValor", "Subtotal")
        texto_completo = texto_completo.replace("Serviços", "")
        texto_completo = texto_completo.replace("Total Nota", "")
        
        # Remove linhas vazias e a parte indesejada do final do texto
        texto_completo = "\n".join(linha for linha in texto_completo.splitlines() if linha.strip())
        inicio_remocao = texto_completo.find("Qt. de Notas:")
        if inicio_remocao != -1:
            texto_completo = texto_completo[:inicio_remocao]

        return texto_completo.strip()  # Remover espaços em branco extras no início e no final do texto
   
def buscaLotesCodigos(texto):
    # Dividir o texto em linhas
    linhas_texto = texto.split('\n')

    ##### Inicio procura a lista de lotes diferentes

    # Criar uma lista para armazenar os diferentes valores de "Lote"
    diferentes_lotes = set()
    # Criar uma lista para armazenar os diferentes valores de "Código"
    diferentes_codigos = set()

    # Iterar pelas linhas (ignorando o cabeçalho)
    for linha in linhas_texto[1:]:
        partes = linha.split()
        if partes[0].isdigit() and len(partes[0]) != 7:
            lote = partes[0]
            diferentes_lotes.add(lote)
        else:
            codigo = partes[0]
            diferentes_codigos.add(codigo)

    # Transformar a lista de lotes em uma lista simples
    lista_diferentes_lotes = list(diferentes_lotes)
    lista_diferentes_codigos = list(diferentes_codigos)

    # print("Lista de diferentes Lotes:", lista_diferentes_lotes)
    # print("Lista de diferentes Códigos:", lista_diferentes_codigos)

    return lista_diferentes_lotes, lista_diferentes_codigos

    ##### FIM procura a lista de lotes diferentes

def tratarTextoExtraido(texto, lista_diferentes_lotes, lista_diferentes_codigos):
    
    # Dividir o texto em linhas
    linhas_texto = texto.split('\n')

    # ##### Inicio junção das linhas que iniciam com lote com as que iniciam com codigos

    # Variável para armazenar as linhas unidas
    linhas_unidas = []

    # Loop para percorrer as linhas
    i = 0
    while i < len(linhas_texto):
        if linhas_texto[i].startswith(tuple(lista_diferentes_lotes)):
        # if any(linha[i].startswith(valor) for valor in valores_verificar):
            # Copiar a linha que começa com "20223"
            linhas_texto[i] = ' '.join(linhas_texto[i].rsplit(' ', 1)[:-1])
            linha_base = linhas_texto[i]
            j = 1
            while i + j < len(linhas_texto) and linhas_texto[i + j].startswith(tuple(lista_diferentes_codigos)):
                # Se a próxima linha inicia com "5000510", "5000518", "5000061" ou "5000517", criar uma nova linha
                nova_linha = linha_base + " " + linhas_texto[i + j]
                if j == 1:
                    nova_linha = ' '.join(nova_linha.rsplit(' ', 1)[:-1])
                linhas_unidas.append(nova_linha)
                j += 1
            # Caso não encontre linhas com "5000510", "5000518", "5000061" ou "5000517", adicionar a linha original à lista de linhas unidas
            if j == 1:
                linhas_unidas.append(linha_base)
            i += j
        else:
            # Caso a linha não inicie com "20223", apenas adicioná-la às linhas unidas
            linhas_unidas.append(linhas_texto[i])
            i += 1

    # Juntar as linhas unidas novamente em um único texto
    texto_processado = '\n'.join(linhas_unidas)

    texto_processado = texto_processado.replace("Lote Nota Data Beneficiário Total Código Qt. Cobr Qt. Paga Valor Qtd CH Subtotal", "Lote Nota Data Hora Lixo1 Beneficiário Código Qtd.Paga Lixo2 Valor Lixo3 Lixo4 Lixo5 Lixo6")

    return texto_processado

def montarDataFrame(lista_diferentes_codigos, texto_processado):

   #### Inicio da montagem do DataFrame

    # Create the regular expression pattern using the list of different codes
    codigo_pattern = '|'.join(lista_diferentes_codigos)


    # Dividir o texto em linhas
    linhas = texto_processado.strip().split('\n')

    # Criar uma lista de dicionários contendo os valores das colunas
    dados = []
    for linha in linhas[1:]:  # Skip the header row

        # Utilizar expressão regular para encontrar a parte desejada da linha
        padrao = re.search(r'((?:' + codigo_pattern + ') \d+,\d+ \d+,\d+ \d+,\d+ \d+,\d+ \d+,\d+ \d+,\d+ \d+,\d+)', linha)
        padrao_beneficiario = re.search(r'\b\d([^\d]+)\b', linha)

        partes = linha.split()
        lote = partes[0]
        data_hora = partes[2] + " " + partes[3] if len(partes) >= 4 else ""

        if padrao_beneficiario:
            beneficiario = padrao_beneficiario.group(1)
        else:
            print("Problema com o Padrão Beneficiário!!!")
            beneficiario = ""


        if padrao:
            parte_desejada = padrao.group(1)
            separados = parte_desejada.split()
            codigo = separados[0]
            qtd_paga = separados[1]
            valor = separados[-5]
        else:
            qtd_paga = ""
            valor = ""
            codigo = ""
            print("Problema com o Padrão!!!")

        dicionario = {
            'Lote': lote,
            'Data-Hora': data_hora,
            'Código': codigo,
            'Beneficiário': beneficiario,
            'Qtd.Paga': qtd_paga,
            'Valor': valor
        }
        dados.append(dicionario)

    # Criar o DataFrame
    df = pd.DataFrame(dados)
    # Limpar espaços em branco no final dos valores da coluna "Beneficiário"
    df['Beneficiário'] = df['Beneficiário'].str.strip()
    
    return df

def filtroAllCodigo(dataFrame, lista_diferentes_codigos):
    # Filtrar o DataFrame com base na lista de códigos
    df_filtered = dataFrame[dataFrame['Código'].isin(lista_diferentes_codigos)]

    # Obter a lista única de beneficiários do DataFrame filtrado
    beneficiarios_unicos = df_filtered['Beneficiário'].unique()

    # Criar um novo DataFrame para armazenar os resultados
    df_result = pd.DataFrame(columns=['Beneficiário'] + lista_diferentes_codigos)

    # Preencher o novo DataFrame com os resultados
    for beneficiario in beneficiarios_unicos:
        row_data = {'Beneficiário': beneficiario}
        for codigo in lista_diferentes_codigos:
            row_data[codigo] = len(df_filtered[(df_filtered['Beneficiário'] == beneficiario) & (df_filtered['Código'] == codigo)])
        df_result = pd.concat([df_result, pd.DataFrame([row_data])], ignore_index=True)

    # Ordenar o DataFrame pelo nome dos beneficiários em ordem alfabética
    df_result = df_result.sort_values(by='Beneficiário', ignore_index=True)

    # Calcular a soma de ocorrências de todos os códigos para cada beneficiário
    df_result['Total'] = df_result[lista_diferentes_codigos].sum(axis=1)


    # Arredondar a soma de ocorrências para remover a casa decimal
    df_result['Total'] = df_result['Total'].astype(int)
        
    # Exibir o novo DataFrame
    # print(df_result)
    return df_result

def filtroByCodigo(dataFrame, codigo):
    
    # Selecione apenas as linhas com o código "5000510"
    df_codigo = dataFrame[dataFrame['Código'] == codigo]

    # Contar a quantidade de ocorrências de cada beneficiário para o código "5000510"
    contagem_ocorrencias = df_codigo['Beneficiário'].value_counts().reset_index()

    # Renomear as colunas do DataFrame resultante
    contagem_ocorrencias.columns = ['Beneficiário', 'Quantas vezes Passou']

    # Exibir o DataFrame resultante
    # print(contagem_ocorrencias)


    # Criando a nova coluna "valor" e atribuindo o valor de 50,00 em todas as linhas
    contagem_ocorrencias['Valor Por Atendimento'] = 50.00

    # Criando as novas colunas "Parceiro 1 - 60%" e "Valor - 40%" com os valores calculados
    contagem_ocorrencias['Parceiro 1 - 60%'] = contagem_ocorrencias['Quantas vezes Passou'] * contagem_ocorrencias['Valor Por Atendimento'] * 0.6
    contagem_ocorrencias['Parceiro 2 - 40%'] = contagem_ocorrencias['Quantas vezes Passou'] * contagem_ocorrencias['Valor Por Atendimento'] * 0.4

    # Formatar as colunas para o formato de moeda (real brasileiro)
    # contagem_ocorrencias['Quantas vezes Passou'] = contagem_ocorrencias['Quantas vezes Passou'].map('R${:,.2f}'.format)
    contagem_ocorrencias['Valor Por Atendimento'] = contagem_ocorrencias['Valor Por Atendimento'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Parceiro 1 - 60%'] = contagem_ocorrencias['Parceiro 1 - 60%'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Parceiro 2 - 40%'] = contagem_ocorrencias['Parceiro 2 - 40%'].map('R$ {:,.2f}'.format)




    # Ordenar o DataFrame pelo nome dos beneficiários em ordem alfabética
    contagem_ocorrencias = contagem_ocorrencias.sort_values(by='Beneficiário', ignore_index=True)

    return contagem_ocorrencias

def filtroByCodigo2(dataFrame, codigo):

    # Lista de beneficiários específicos
    beneficiarios_especificos = ["CECILIA PEREIRA MACHADO", "JOAO MIGUEL PARENTE GOMES"]

    # Selecione apenas as linhas com o código "5000510"
    df_codigo = dataFrame[dataFrame['Código'] == codigo]
    
    # Contar a quantidade de ocorrências de cada beneficiário para o código "5000510"
    contagem_ocorrencias = df_codigo['Beneficiário'].value_counts().reset_index()

    # Renomear as colunas do DataFrame resultante
    contagem_ocorrencias.columns = ['Beneficiário', 'Quantas vezes Passou']


    

    # print(contagem_ocorrencias)

    #     # Verificando se os beneficiários estão no DataFrame
    # for beneficiario in beneficiarios_especificos:
    #     if beneficiario in contagem_ocorrencias["Beneficiário"].values:
    #         print(f"{beneficiario} está presente no DataFrame.")
    #     else:
    #         print(f"{beneficiario} não está presente no DataFrame.")

    # Criando a nova coluna "Valor Por Atendimento" e atribuindo o valor de 50,00 em todas as linhas
    contagem_ocorrencias['Valor Por Atendimento'] = 50.00

    
    # Função para calcular os valores específicos para os beneficiários "CECILIA PEREIRA MACHADO" e "JOAO MIGUEL PARENTE GOMES"
    def calcular_valores(row):
        if row['Beneficiário'] in beneficiarios_especificos:
            parceiro_1 = row['Quantas vezes Passou'] * row['Valor Por Atendimento'] * 0.5
            parceiro_2 = row['Quantas vezes Passou'] * row['Valor Por Atendimento'] * 0.4
        else:
            parceiro_1 = row['Quantas vezes Passou'] * row['Valor Por Atendimento'] * 0.6
            parceiro_2 = row['Quantas vezes Passou'] * row['Valor Por Atendimento'] * 0.4

        recebido = row['Quantas vezes Passou'] * row['Valor Por Atendimento']
        devido = 40 * 50.00 if row['Beneficiário'] in beneficiarios_especificos else 0.00
        mae_faltou = recebido - devido if row['Beneficiário'] in beneficiarios_especificos else 0.00
        return pd.Series({'Recebido': recebido, 'Devido': devido, 'Mãe Faltou': mae_faltou, 'Parceiro 1 - 60%': parceiro_1, 'Parceiro 2 - 40%': parceiro_2})

    # Aplicando a função aos dados do DataFrame para calcular as colunas "Recebido", "Devido", "Mãe Faltou", "Parceiro 1 - 60%" e "Parceiro 2 - 40%"
    contagem_ocorrencias[['Recebido', 'Devido', 'Mãe Faltou', 'Parceiro 1 - 60%', 'Parceiro 2 - 40%']] = contagem_ocorrencias.apply(calcular_valores, axis=1)

    # Formatar as colunas para o formato de moeda (real brasileiro)
    # contagem_ocorrencias['Quantas vezes Passou'] = contagem_ocorrencias['Quantas vezes Passou'].map('R${:,.2f}'.format)
    contagem_ocorrencias['Valor Por Atendimento'] = contagem_ocorrencias['Valor Por Atendimento'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Recebido'] = contagem_ocorrencias['Recebido'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Devido'] = contagem_ocorrencias['Devido'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Mãe Faltou'] = contagem_ocorrencias['Mãe Faltou'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Parceiro 1 - 60%'] = contagem_ocorrencias['Parceiro 1 - 60%'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Parceiro 2 - 40%'] = contagem_ocorrencias['Parceiro 2 - 40%'].map('R$ {:,.2f}'.format)


    # Ordenar o DataFrame pelo nome dos beneficiários em ordem alfabética
    contagem_ocorrencias = contagem_ocorrencias.sort_values(by='Beneficiário', ignore_index=True)

    return contagem_ocorrencias


def filtroByAT(dataFrame, beneficiarios_desejados, codigo):
    
    # Lista de beneficiários específicos
    beneficiarios_especificos = ["CECILIA PEREIRA MACHADO", "JOAO MIGUEL PARENTE GOMES"]

    # Selecione apenas as linhas com o código "5000510"
    df_codigo = dataFrame[dataFrame['Código'] == codigo]
    
    # Contar a quantidade de ocorrências de cada beneficiário para o código "5000510"
    contagem_ocorrencias = df_codigo['Beneficiário'].value_counts().reset_index()

    # Renomear as colunas do DataFrame resultante
    contagem_ocorrencias.columns = ['Beneficiário', 'Quantas vezes Passou']

    print(contagem_ocorrencias)

    # Filtro para manter apenas as linhas cujo beneficiário está na lista de beneficiários específicos
    filtro = contagem_ocorrencias["Beneficiário"].isin(beneficiarios_desejados)

    # Aplicar o filtro ao DataFrame
    contagem_ocorrencias = contagem_ocorrencias[filtro]

    print(contagem_ocorrencias)

    print("aqui")
    

    # print(contagem_ocorrencias)

    #     # Verificando se os beneficiários estão no DataFrame
    # for beneficiario in beneficiarios_especificos:
    #     if beneficiario in contagem_ocorrencias["Beneficiário"].values:
    #         print(f"{beneficiario} está presente no DataFrame.")
    #     else:
    #         print(f"{beneficiario} não está presente no DataFrame.")

    # Criando a nova coluna "Valor Por Atendimento" e atribuindo o valor de 50,00 em todas as linhas
    contagem_ocorrencias['Valor Por Atendimento'] = 50.00

    
    # Função para calcular os valores específicos para os beneficiários "CECILIA PEREIRA MACHADO" e "JOAO MIGUEL PARENTE GOMES"
    def calcular_valores(row):
        if row['Beneficiário'] in beneficiarios_desejados:
            parceiro_1 = row['Quantas vezes Passou'] * row['Valor Por Atendimento'] * 0.5
            parceiro_2 = row['Quantas vezes Passou'] * row['Valor Por Atendimento'] * 0.4
        else:
            parceiro_1 = row['Quantas vezes Passou'] * row['Valor Por Atendimento'] * 0.6
            parceiro_2 = row['Quantas vezes Passou'] * row['Valor Por Atendimento'] * 0.4

        recebido = row['Quantas vezes Passou'] * row['Valor Por Atendimento']
        devido = 40 * 50.00 if row['Beneficiário'] in beneficiarios_especificos else 0.00
        mae_faltou = recebido - devido if row['Beneficiário'] in beneficiarios_especificos else 0.00
        return pd.Series({'Recebido': recebido, 'Devido': devido, 'Mãe Faltou': mae_faltou, 'Parceiro 1 - 60%': parceiro_1, 'Parceiro 2 - 40%': parceiro_2})

    # Aplicando a função aos dados do DataFrame para calcular as colunas "Recebido", "Devido", "Mãe Faltou", "Parceiro 1 - 60%" e "Parceiro 2 - 40%"
    contagem_ocorrencias[['Recebido', 'Devido', 'Mãe Faltou', 'Parceiro 1 - 60%', 'Parceiro 2 - 40%']] = contagem_ocorrencias.apply(calcular_valores, axis=1)

    # Formatar as colunas para o formato de moeda (real brasileiro)
    # contagem_ocorrencias['Quantas vezes Passou'] = contagem_ocorrencias['Quantas vezes Passou'].map('R${:,.2f}'.format)
    contagem_ocorrencias['Valor Por Atendimento'] = contagem_ocorrencias['Valor Por Atendimento'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Recebido'] = contagem_ocorrencias['Recebido'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Devido'] = contagem_ocorrencias['Devido'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Mãe Faltou'] = contagem_ocorrencias['Mãe Faltou'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Parceiro 1 - 60%'] = contagem_ocorrencias['Parceiro 1 - 60%'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Parceiro 2 - 40%'] = contagem_ocorrencias['Parceiro 2 - 40%'].map('R$ {:,.2f}'.format)

    # Ordenar o DataFrame pelo nome dos beneficiários em ordem alfabética
    contagem_ocorrencias = contagem_ocorrencias.sort_values(by='Beneficiário', ignore_index=True)

    return contagem_ocorrencias


@app.route('/', methods=['GET', 'POST'])
def index():
    global DATAFRAME_ORIGINAL
    global DATAFRAME_INDEX

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

            # Convert the DataFrame to an HTML table
            # df_html = df_exibir.to_html(classes='table table-bordered table-striped', index=False)
            # return jsonify(df_html)
            return render_template('result.html', table=df_exibir.to_html(classes='table table-bordered table-striped'))

    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    global DATAFRAME_ORIGINAL
    global DATAFRAME_INDEX

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

            
            return render_template('result.html', table=df_exibir.to_html(classes='table table-bordered table-striped'))
    return render_template('home.html')

@app.route('/filtro-5000510', methods=['GET'])
def filtro_codigo_5000510():
    global DATAFRAME_ORIGINAL
    if DATAFRAME_ORIGINAL is None:
        return "No dataframe available."
    df_exibir = filtroByCodigo(DATAFRAME_ORIGINAL, codigo="5000510")
    df_html = df_exibir.to_html(classes='table table-bordered table-striped center-align', index=False)
    return render_template('filtro_codigo.html', df_html=df_html, df_index=DATAFRAME_INDEX)

@app.route('/filtro-elizza', methods=['GET'])
def filtro_elizza():
    global DATAFRAME_ORIGINAL
    if DATAFRAME_ORIGINAL is None:
        return "No dataframe available."
    # print(DATAFRAME_ORIGINAL)
    # Fazendo o filtro com base nos beneficiários desejados
    beneficiarios_desejados = ["ARTHUR MIGUEL C QUEIROZ", "CAIO ALMEIDA CARNEIRO", "CECILIA PEREIRA MACHADO",
                                 "ERIC ALMEIDA CARNEIRO", "JOAO GUILHERME S SANTOS", "JOAO LUCAS D QUEIROZ", 
                                 "JOAO MIGUEL PARENTE GOMES", "LUIZ GABRIEL O ALVES", "YAN LUCCA LEMOS GOMES", "JAMILY COSTA SALDANHA"]
    
    codigo = "5000510"
    df_exibir = filtroByAT(DATAFRAME_ORIGINAL, beneficiarios_desejados, codigo)
    df_html = df_exibir.to_html(classes='table table-bordered table-striped', index=False)
    # return render_template('filtro_codigo.html', df_html=df_html)
    return render_template('result.html', table=df_exibir.to_html(classes='table table-bordered table-striped'))


# @app.route('/home', methods=['GET'])
# def home():
#     global DATAFRAME_INDEX 

            
#     return render_template('result.html', table=DATAFRAME_INDEX.to_html(classes='table table-bordered table-striped'))
    

@app.route('/filtro-5000518', methods=['GET'])
def filtro_codigo_5000518():
    global DATAFRAME_ORIGINAL
    df_exibir = filtroByCodigo(DATAFRAME_ORIGINAL, codigo="5000518")
    df_html = df_exibir.to_html(classes='table table-bordered table-striped', index=False)
    return render_template('filtro_codigo.html', df_html=df_html)


if __name__ == '__main__':
    app.run(debug=True)




