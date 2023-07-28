import pandas as pd
  

# Define a function to format the values in Brazilian style
def format_brazilian_currency(value):
    return 'R$ {:,.2f}'.format(value).replace('.', '*').replace(',', '.').replace('*', ',')


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
    contagem_ocorrencias.columns = ['Beneficiário', 'Quantidade']

    # Exibir o DataFrame resultante
    # print(contagem_ocorrencias)


    # Criando a nova coluna "valor" e atribuindo o valor de 50,00 em todas as linhas
    contagem_ocorrencias['Valor/Atendimento'] = 50.00

    # Criando as novas colunas "Parceiro 1 - 60%" e "Valor - 40%" com os valores calculados
    contagem_ocorrencias['Parceiro - 60%'] = contagem_ocorrencias['Quantidade'] * contagem_ocorrencias['Valor/Atendimento'] * 0.6
    contagem_ocorrencias['Parceiro - 40%'] = contagem_ocorrencias['Quantidade'] * contagem_ocorrencias['Valor/Atendimento'] * 0.4

    # Formatar as colunas para o formato de moeda (real brasileiro)
    # contagem_ocorrencias['Quantidade'] = contagem_ocorrencias['Quantidade'].map('R${:,.2f}'.format)
    contagem_ocorrencias['Valor/Atendimento'] = contagem_ocorrencias['Valor/Atendimento'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Parceiro - 60%'] = contagem_ocorrencias['Parceiro - 60%'].map('R$ {:,.2f}'.format)
    contagem_ocorrencias['Parceiro - 40%'] = contagem_ocorrencias['Parceiro - 40%'].map('R$ {:,.2f}'.format)




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
    contagem_ocorrencias.columns = ['Beneficiário', 'Quantidade']


    

    # print(contagem_ocorrencias)

    #     # Verificando se os beneficiários estão no DataFrame
    # for beneficiario in beneficiarios_especificos:
    #     if beneficiario in contagem_ocorrencias["Beneficiário"].values:
    #         print(f"{beneficiario} está presente no DataFrame.")
    #     else:
    #         print(f"{beneficiario} não está presente no DataFrame.")

    # Criando a nova coluna "Valor/Atendimento" e atribuindo o valor de 50,00 em todas as linhas
    contagem_ocorrencias['Valor/Atendimento'] = 50.00

    
    # Função para calcular os valores específicos para os beneficiários "CECILIA PEREIRA MACHADO" e "JOAO MIGUEL PARENTE GOMES"
    def calcular_valores(row):
        if row['Beneficiário'] in beneficiarios_especificos:
            parceiro_1 = row['Quantidade'] * row['Valor/Atendimento'] * 0.5
            parceiro_2 = row['Quantidade'] * row['Valor/Atendimento'] * 0.4
        else:
            parceiro_1 = row['Quantidade'] * row['Valor/Atendimento'] * 0.6
            parceiro_2 = row['Quantidade'] * row['Valor/Atendimento'] * 0.4

        recebido = row['Quantidade'] * row['Valor/Atendimento']
        devido = 40 * 50.00 if row['Beneficiário'] in beneficiarios_especificos else 0.00
        mae_faltou = recebido - devido if row['Beneficiário'] in beneficiarios_especificos else 0.00
        return pd.Series({'Recebido': recebido, 'Devido': devido, 'Saldo Mãe': mae_faltou, 'Parceiro - 60%': parceiro_1, 'Parceiro - 40%': parceiro_2})

    # Aplicando a função aos dados do DataFrame para calcular as colunas "Recebido", "Devido", "Saldo Mãe", "Parceiro 1 - 60%" e "Parceiro 2 - 40%"
    contagem_ocorrencias[['Recebido', 'Devido', 'Saldo Mãe', 'Parceiro - 60%', 'Parceiro - 40%']] = contagem_ocorrencias.apply(calcular_valores, axis=1)

    # Formatar as colunas para o formato de moeda (real brasileiro)
    # contagem_ocorrencias['Quantidade'] = contagem_ocorrencias['Quantidade'].map('R${:,.2f}'.format)
    contagem_ocorrencias['Valor/Atendimento'] = contagem_ocorrencias['Valor/Atendimento'].apply(format_brazilian_currency)
    contagem_ocorrencias['Recebido'] = contagem_ocorrencias['Recebido'].apply(format_brazilian_currency)
    contagem_ocorrencias['Devido'] = contagem_ocorrencias['Devido'].apply(format_brazilian_currency)
    contagem_ocorrencias['Saldo Mãe'] = contagem_ocorrencias['Saldo Mãe'].apply(format_brazilian_currency)
    contagem_ocorrencias['Parceiro - 60%'] = contagem_ocorrencias['Parceiro - 60%'].apply(format_brazilian_currency)
    contagem_ocorrencias['Parceiro - 40%'] = contagem_ocorrencias['Parceiro - 40%'].apply(format_brazilian_currency)


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
    contagem_ocorrencias.columns = ['Beneficiário', 'Quantidade']

    # print(contagem_ocorrencias)

    # Filtro para manter apenas as linhas cujo beneficiário está na lista de beneficiários específicos
    filtro = contagem_ocorrencias["Beneficiário"].isin(beneficiarios_desejados)

    # Aplicar o filtro ao DataFrame
    contagem_ocorrencias = contagem_ocorrencias[filtro]

    # print(contagem_ocorrencias)

    # print("aqui")
    

    # print(contagem_ocorrencias)

    #     # Verificando se os beneficiários estão no DataFrame
    # for beneficiario in beneficiarios_especificos:
    #     if beneficiario in contagem_ocorrencias["Beneficiário"].values:
    #         print(f"{beneficiario} está presente no DataFrame.")
    #     else:
    #         print(f"{beneficiario} não está presente no DataFrame.")

    # Criando a nova coluna "Valor/Atendimento" e atribuindo o valor de 50,00 em todas as linhas
    contagem_ocorrencias['Valor/Atendimento'] = 50.00

    
    # Função para calcular os valores específicos para os beneficiários "CECILIA PEREIRA MACHADO" e "JOAO MIGUEL PARENTE GOMES"
    def calcular_valores(row):
        if row['Beneficiário'] in beneficiarios_especificos:
            parceiro_1 = row['Quantidade'] * row['Valor/Atendimento'] * 0.5
            parceiro_2 = row['Quantidade'] * row['Valor/Atendimento'] * 0.4
        else:
            parceiro_1 = row['Quantidade'] * row['Valor/Atendimento'] * 0.6
            parceiro_2 = row['Quantidade'] * row['Valor/Atendimento'] * 0.4

        recebido = row['Quantidade'] * row['Valor/Atendimento']
        devido = 40 * 50.00 if row['Beneficiário'] in beneficiarios_especificos else 0.00
        mae_faltou = recebido - devido if row['Beneficiário'] in beneficiarios_especificos else 0.00
        return pd.Series({'Recebido': recebido, 'Devido': devido, 'Saldo Mãe': mae_faltou, 'Parceiro - 60%': parceiro_1, 'Parceiro - 40%': parceiro_2})

    # Aplicando a função aos dados do DataFrame para calcular as colunas "Recebido", "Devido", "Saldo Mãe", "Parceiro 1 - 60%" e "Parceiro 2 - 40%"
    contagem_ocorrencias[['Recebido', 'Devido', 'Saldo Mãe', 'Parceiro - 60%', 'Parceiro - 40%']] = contagem_ocorrencias.apply(calcular_valores, axis=1)

    # print(contagem_ocorrencias)

    # Ordenar o DataFrame pelo nome dos beneficiários em ordem alfabética
    contagem_ocorrencias = contagem_ocorrencias.sort_values(by='Beneficiário', ignore_index=True)

    # Calcular os totais das colunas
    total_quantas_vezes_passou = contagem_ocorrencias["Quantidade"].sum()
    total_recebido = contagem_ocorrencias["Recebido"].sum()
    total_devido = contagem_ocorrencias["Devido"].sum()
    total_mae_faltou = contagem_ocorrencias["Saldo Mãe"].sum()
    total_parceiro_1 = contagem_ocorrencias["Parceiro - 60%"].sum()
    total_parceiro_2 = contagem_ocorrencias["Parceiro - 40%"].sum()

    # Criar a nova linha
    total_row = {
        "Beneficiário": "Total",
        "Quantidade": total_quantas_vezes_passou,
        "Valor/Atendimento": 50.0,
        "Recebido": total_recebido,
        "Devido": total_devido,
        "Saldo Mãe": total_mae_faltou,
        "Parceiro - 60%": total_parceiro_1,
        "Parceiro - 40%": total_parceiro_2
    }

    # Concatenar o DataFrame com a nova linha
    contagem_ocorrencias = pd.concat([contagem_ocorrencias, pd.DataFrame(total_row, index=[len(contagem_ocorrencias)])])

    # Resetar o índice do DataFrame resultante
    contagem_ocorrencias.reset_index(drop=True, inplace=True)

    print(contagem_ocorrencias)

    

    # Formatar as colunas para o formato de moeda (real brasileiro)
    # contagem_ocorrencias['Quantidade'] = contagem_ocorrencias['Quantidade'].map('R${:,.2f}'.format)
    contagem_ocorrencias['Valor/Atendimento'] = contagem_ocorrencias['Valor/Atendimento'].apply(format_brazilian_currency)
    contagem_ocorrencias['Recebido'] = contagem_ocorrencias['Recebido'].apply(format_brazilian_currency)
    contagem_ocorrencias['Devido'] = contagem_ocorrencias['Devido'].apply(format_brazilian_currency)
    contagem_ocorrencias['Saldo Mãe'] = contagem_ocorrencias['Saldo Mãe'].apply(format_brazilian_currency)
    contagem_ocorrencias['Parceiro - 60%'] = contagem_ocorrencias['Parceiro - 60%'].apply(format_brazilian_currency)
    contagem_ocorrencias['Parceiro - 40%'] = contagem_ocorrencias['Parceiro - 40%'].apply(format_brazilian_currency)

    print(contagem_ocorrencias)
    # Formatar as colunas para o formato de moeda (real brasileiro)
# df['Quantas vezes Passou'] = df['Quantas vezes Passou'].map('R${:,.2f}'.format)
# df['Valor'] = df['Valor'].map('R${:,.2f}'.format)
# df['Recebido'] = df['Recebido'].map('R${:,.2f}'.format)
# df['Parceiro 1 - 60%'] = df['Parceiro 1 - 60%'].map('R${:,.2f}'.format)
# df['Valor - 40%'] = df['Valor - 40%'].map('R${:,.2f}'.format)

    return contagem_ocorrencias
