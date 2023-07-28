
import re
import pandas as pd

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