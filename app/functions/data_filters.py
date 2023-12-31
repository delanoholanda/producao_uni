import pandas as pd
from models import db, Profissional, Beneficiario, Producao, DadosProducao
  

# Define a function to format the values in Brazilian style
def format_brazilian_currency(value):
    return 'R$ {:,.2f}'.format(value).replace('.', '*').replace(',', '.').replace('*', ',')

    
# Função para formatar os valores da coluna "Quantidade"
def format_quantity(quantity):
    if isinstance(quantity, float):
        if quantity.is_integer():
            return f"{int(quantity)}"
        else:
            return f"{quantity:.1f}".replace('.', ',')
    return f"{quantity}"


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


def montarDataFrameFinal(contagem_ocorrencias, beneficiarios_especificos):
    
    # Função para calcular os valores específicos para os beneficiários "CECILIA PEREIRA MACHADO" e "JOAO MIGUEL PARENTE GOMES"
    def calcular_valores(row):
        if row['Beneficiário'] in beneficiarios_especificos:
            parceiro_1 = row['Quantidade'] * row['Valor/Atendimento'] * 0.5
            parceiro_2 = row['Quantidade'] * row['Valor/Atendimento'] * 0.4
        else:
            parceiro_1 = row['Quantidade'] * row['Valor/Atendimento'] * 0.6
            parceiro_2 = row['Quantidade'] * row['Valor/Atendimento'] * 0.4

        recebido = row['Quantidade'] * row['Valor/Atendimento']
        devido = 40 * 50.00 if row['Beneficiário'] in beneficiarios_especificos else row['Quantidade'] * row['Valor/Atendimento']
        mae_faltou = recebido - devido # if row['Beneficiário'] in beneficiarios_especificos else 0.00
        
        return pd.Series({
            'Recebido': recebido,
            'Devido': devido,
            'Saldo Mãe': mae_faltou,
            'Parceiro - 60%': parceiro_1,
            'Parceiro - 40%': parceiro_2})

    # Aplicando a função aos dados do DataFrame para calcular as colunas "Recebido", "Devido", "Saldo Mãe", "Parceiro 1 - 60%" e "Parceiro 2 - 40%"
    contagem_ocorrencias[['Recebido', 'Devido', 'Saldo Mãe', 'Parceiro - 60%', 'Parceiro - 40%']] = contagem_ocorrencias.apply(calcular_valores, axis=1)

    # Criando a nova coluna "Imposto Retido" e calculando o valor
    contagem_ocorrencias['Imposto Retido'] = contagem_ocorrencias['Quantidade'] * 5.02
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
    total_retido = contagem_ocorrencias["Imposto Retido"].sum()

    # Criar a nova linha
    total_row = {
        "Beneficiário": "Total",
        "Quantidade": total_quantas_vezes_passou,
        "Valor/Atendimento": 50.0,
        "Tipo": "",
        "Recebido": total_recebido,
        "Devido": total_devido,
        "Saldo Mãe": total_mae_faltou,
        "Parceiro - 60%": total_parceiro_1,
        "Parceiro - 40%": total_parceiro_2,
        "Imposto Retido": total_retido
    }

    # Concatenar o DataFrame com a nova linha
    contagem_ocorrencias = pd.concat([contagem_ocorrencias, pd.DataFrame(total_row, index=[len(contagem_ocorrencias)])])

    # Resetar o índice do DataFrame resultante
    contagem_ocorrencias.reset_index(drop=True, inplace=True)

    # print(contagem_ocorrencias)

    
    # Aplicar a função de formatação à coluna "Quantidade"
    contagem_ocorrencias["Quantidade"] = contagem_ocorrencias["Quantidade"].apply(format_quantity)

    # Formatar as colunas para o formato de moeda (real brasileiro)
    # contagem_ocorrencias['Quantidade'] = contagem_ocorrencias['Quantidade'].map('R${:,.2f}'.format)
    contagem_ocorrencias['Valor/Atendimento'] = contagem_ocorrencias['Valor/Atendimento'].apply(format_brazilian_currency)
    contagem_ocorrencias['Recebido'] = contagem_ocorrencias['Recebido'].apply(format_brazilian_currency)
    contagem_ocorrencias['Devido'] = contagem_ocorrencias['Devido'].apply(format_brazilian_currency)
    contagem_ocorrencias['Saldo Mãe'] = contagem_ocorrencias['Saldo Mãe'].apply(format_brazilian_currency)
    contagem_ocorrencias['Parceiro - 60%'] = contagem_ocorrencias['Parceiro - 60%'].apply(format_brazilian_currency)
    contagem_ocorrencias['Parceiro - 40%'] = contagem_ocorrencias['Parceiro - 40%'].apply(format_brazilian_currency)
    contagem_ocorrencias['Imposto Retido'] = contagem_ocorrencias['Imposto Retido'].apply(format_brazilian_currency)

    return contagem_ocorrencias


def filtroByCodigo2(dataFrame, codigo, beneficiarios_especificos):

    # Selecione apenas as linhas com o código "5000510"
    df_codigo = dataFrame[dataFrame['Código'] == codigo]
    
    # Contar a quantidade de ocorrências de cada beneficiário para o código "5000510"
    contagem_ocorrencias = df_codigo['Beneficiário'].value_counts().reset_index()

    # Renomear as colunas do DataFrame resultante
    contagem_ocorrencias.columns = ['Beneficiário', 'Quantidade']

    # Criando a nova coluna "Valor/Atendimento" e atribuindo o valor de 50,00 em todas as linhas
    contagem_ocorrencias['Valor/Atendimento'] = 50.00

    # Adding the new column "Tipo"
    def define_tipo(row):
        if row['Beneficiário'] in beneficiarios_especificos:
            return "AT"
        else:
            return "Clinica"

    contagem_ocorrencias['Tipo'] = contagem_ocorrencias.apply(define_tipo, axis=1)

    contagem_ocorrencias = montarDataFrameFinal(contagem_ocorrencias,beneficiarios_especificos)

    return contagem_ocorrencias


def filtroByAT(dataFrame, beneficiarios_desejados, beneficiarios_especificos, codigo, profissional):

    # Selecione apenas as linhas com o código "5000510"
    df_codigo = dataFrame[dataFrame['Código'] == codigo]
    
    # Contar a quantidade de ocorrências de cada beneficiário para o código "5000510"
    contagem_ocorrencias = df_codigo['Beneficiário'].value_counts().reset_index()

    # Renomear as colunas do DataFrame resultante
    contagem_ocorrencias.columns = ['Beneficiário', 'Quantidade']

    # Filtro para manter apenas as linhas cujo beneficiário está na lista de beneficiários específicos
    filtro = contagem_ocorrencias["Beneficiário"].isin(beneficiarios_desejados)

    # Aplicar o filtro ao DataFrame
    contagem_ocorrencias = contagem_ocorrencias[filtro]


    # Verificar se o DataFrame filtrado está vazio
    if contagem_ocorrencias.empty:
        # print("Nenhum beneficiário encontrado na lista de beneficiários desejados.")
        return contagem_ocorrencias
        # Aqui você pode definir uma ação alternativa, como atribuir outro DataFrame ou sair do programa.
    else:
        # Criando a nova coluna "Valor/Atendimento" e atribuindo o valor de 50,00 em todas as linhas
        contagem_ocorrencias['Valor/Atendimento'] = 50.00

        # Adding the new column "Tipo"
        def define_tipo(row):
            if row['Beneficiário'] in beneficiarios_especificos:
                return "AT"
            else:
                return "Clinica"

        contagem_ocorrencias['Tipo'] = contagem_ocorrencias.apply(define_tipo, axis=1)        

        if profissional == "Elizza":
            # Alterar os valores na coluna "Quantas vezes Passou"
            contagem_ocorrencias.loc[contagem_ocorrencias["Beneficiário"].isin(["CAIO ALMEIDA CARNEIRO", "ERIC ALMEIDA CARNEIRO", "ARTHUR MIGUEL C QUEIROZ"]), "Quantidade"] /= 2
            
        elif profissional == "Gabriela":
            contagem_ocorrencias.loc[contagem_ocorrencias["Beneficiário"].isin(["ARTHUR MIGUEL C QUEIROZ", "CARLOS HENRIK O BATISTA"]), "Quantidade"] /= 2

        contagem_ocorrencias = montarDataFrameFinal(contagem_ocorrencias,beneficiarios_especificos)

        return contagem_ocorrencias


def filtroByAtBd(beneficiarios_especificos, beneficiarios_desejados, codigo, profissional, producao):

    # print("---------------------------------------------------------------")
    
    # Inicialize uma lista para armazenar os IDs correspondentes
    beneficiarios = []

    # Itere pelos nomes desejados e encontre os IDs correspondentes
    for nome_desejado in beneficiarios_desejados:
        beneficiario = Beneficiario.query.filter_by(nome=nome_desejado).first()
        if beneficiario:
            beneficiarios.append(beneficiario)

    # Query the database to get DadosProducao records with the specified 'codigo' and 'producao_id'
    dados_producao_records = DadosProducao.query.filter_by(codigo=codigo).filter_by(producao_id=producao.id).all()

    # Create a dictionary to store beneficiary counts
    beneficiary_counts = {}

    # Count the occurrences of each beneficiary
    for record in dados_producao_records:
        if record.beneficiario_id in beneficiary_counts:
            beneficiary_counts[record.beneficiario_id] += 1
        else:
            beneficiary_counts[record.beneficiario_id] = 1
    
    ids_desejados = []
    # Itere pelos nomes desejados e encontre os IDs correspondentes
    for nome_desejado in beneficiarios_desejados:
        beneficiario = Beneficiario.query.filter_by(nome=nome_desejado).first()
        if beneficiario:
            ids_desejados.append(beneficiario.id)

    # Filter beneficiaries based on 'beneficiarios_desejados'
    filtered_beneficiaries = [
        (beneficiary.nome, beneficiary_counts.get(beneficiary.id, 0))
        for beneficiary in beneficiarios
        if beneficiary.id in ids_desejados
    ]

    # Sort filtered_beneficiaries alphabetically by beneficiary name
    filtered_beneficiaries.sort(key=lambda x: x[0])

    # # Create the result list with necessary columns
    # result = []
    # total_quantity = 0  # Inicialize a variável para a soma das quantidades

    # for beneficiary, count in filtered_beneficiaries:
    #     result.append({
    #         'Beneficiário': beneficiary,
    #         'Quantidade': count,
    #         'Valor/Atendimento': 50.00,
    #         'Tipo': 'AT' if beneficiary in beneficiarios_especificos else 'Clinica'
    #     })

    #     # Adicione a quantidade atual à soma total
    #     total_quantity += count

    # # Adicione a linha "Total" ao resultado
    # result.append({
    #     'Beneficiário': 'Total',
    #     'Quantidade': total_quantity,
    #     'Valor/Atendimento': 50.00,
    #     'Tipo': '--'
    # })

    # Apply specific logic based on 'profissional'
    if profissional == "Elizza":
        for i, (beneficiary, count) in enumerate(filtered_beneficiaries):
            if beneficiary in ["CAIO ALMEIDA CARNEIRO", "ERIC ALMEIDA CARNEIRO"]:
                if beneficiary == "ARTHUR MIGUEL C QUEIROZ":
                    filtered_beneficiaries[i] = (beneficiary, (count / 2) + 1)
                # elif beneficiary == "YAN LUCCA LEMOS GOMES":
                    # filtered_beneficiaries[i] = (beneficiary, 14)
                else:
                    filtered_beneficiaries[i] = (beneficiary, count / 2) 
    elif profissional == "Gabriela":
        for i, (beneficiary, count) in enumerate(filtered_beneficiaries):
            if beneficiary in ["ARTHUR MIGUEL C QUEIROZ", "CARLOS HENRIK O BATISTA"]:
                filtered_beneficiaries[i] = (beneficiary, count / 2)

    # Create the result list with necessary columns
    result = []
    total_quantity = 0  # Inicialize a variável para a soma das quantidades
    total_recebido = 0  # Inicialize a variável para a soma das quantidades
    total_devido = 0  # Inicialize a variável para a soma das quantidades
    total_mae = 0  # Inicialize a variável para a soma das quantidades
    total_parceiro_60 = 0  # Inicialize a variável para a soma das quantidades
    total_parceiro_40 = 0  # Inicialize a variável para a soma das quantidades
    total_imposto = 0

    for beneficiary, count in filtered_beneficiaries:
        # Calcule os valores
        received = count * 50.00
        imposto = count * 5.02
        due = 40 * 50.00 if beneficiary in beneficiarios_especificos else count * 50.00
        mother_balance = received - due
        if beneficiary in beneficiarios_especificos:
            if (count * 50.00) > 2000:
                partner_60 = 1000
                partner_40 = received - partner_60
            elif (count * 50.00) < 2000:
                partner_40 = 1000
                partner_60 = received - partner_40
            elif(count * 50.00) == 2000:
                partner_40 = 1000
                partner_60 = 1000            
        else:
            partner_60 = count * 50.00 * 0.6
            partner_40 = count * 50.00 * 0.4       
        

        result.append({
            'Beneficiário': beneficiary,
            'Quantidade': count,
            'Valor/Atendimento': 50.00,
            'Tipo': 'AT' if beneficiary in beneficiarios_especificos else 'Clinica',
            'Recebido': received,
            'Devido': due,
            'Saldo Mãe': mother_balance,
            'Parceiro - 60%': partner_60,
            'Parceiro - 40%': partner_40,
            'Imposto Retido': imposto
        })

        # Adicione a quantidade atual à soma total
        total_quantity += count
        total_recebido += received
        total_devido += due
        total_mae += mother_balance
        total_parceiro_60 += partner_60
        total_parceiro_40 += partner_40
        total_imposto += imposto

    # Adicione a linha "Total" ao resultado
    result.append({
        'Beneficiário': 'Total',
        'Quantidade': total_quantity,
        'Valor/Atendimento': 50.00,
        'Tipo': '',
        'Recebido': total_recebido,
        'Devido': total_devido,
        'Saldo Mãe': total_mae,
        'Parceiro - 60%': total_parceiro_60,
        'Parceiro - 40%': total_parceiro_40,
        'Imposto Retido': total_imposto
    })
    
    # return pd.Series({
    #     'Recebido': recebido,
    #     'Devido': devido,
    #     'Saldo Mãe': mae_faltou,
    #     'Parceiro - 60%': parceiro_1,
    #     'Parceiro - 40%': parceiro_2})

    # Print the records
    # for b in result:
        # print(b)

    # # Criar a nova linha
    # total_row = {
    #     "Beneficiário": "Total",
    #     "Quantidade": total_quantas_vezes_passou,
    #     "Valor/Atendimento": 50.0,
    #     "Tipo": "",
    #     "Recebido": total_recebido,
    #     "Devido": total_devido,
    #     "Saldo Mãe": total_mae_faltou,
    #     "Parceiro - 60%": total_parceiro_1,
    #     "Parceiro - 40%": total_parceiro_2,
    #     "Imposto Retido": total_retido
    # }
    

    print("---------------------------------------------------------------")
    return result



def obter_beneficiarios_desejados(profissional):
    if profissional == "Elizza":
        beneficiarios_desejados = [
            "ARTHUR MIGUEL C QUEIROZ", "CAIO ALMEIDA CARNEIRO", "CECILIA PEREIRA MACHADO",
            "ERIC ALMEIDA CARNEIRO", "JOAO GUILHERME S SANTOS", "JOAO LUCAS D QUEIROZ",
            "JOAO MIGUEL PARENTE GOMES", "LUIZ GABRIEL O ALVES", "YAN LUCCA LEMOS GOMES",
            "CARLOS EDUARDO A OLIVEIRA" , "MARIA LUIZA LOPES MARTINS"]
    elif profissional == "Gabriela":
        beneficiarios_desejados = [
            "ARTHUR DE LIMA VILAR", "ARTHUR MOREIRA CASTRO", "CARLOS HENRIK O BATISTA",
            "ALVARO WESLEY SILVA LEMOS", "FRANCISCO RAFAEL P SILVA", "ISIS MARIA DANTAS SOARES",
            "JOAO ERNANDO LOPES LIMA", "JOAO MIGUEL N DE ASSIS", "MANUEL IDEFONSO DA CUNHA",
            "MARIA ISABELLY GOMES LIMA", "NOAH OLIVEIRA RODRIGUES", "OSAIAS ALMEIDA CASTRO NT",
            "WILLIAM LEVY C DE BRITO", "YAN WEVERTON BATISTA MELO", "ARTHUR MIGUEL C QUEIROZ"]
    elif profissional == "Joana":
        beneficiarios_desejados = [
            "ANTONIO SAULO F ALMEIDA", "JAMILY COSTA SALDANHA", "PEDRO DE ALMEIDA AVELINO"]
    elif profissional == "Darlene":
        beneficiarios_desejados = [
            "ANTONIO GABRIEL P SILVA", "EMANUEL IGOR P FERNANDES", "FRANCISCO DEIVYD O SOUSA",
            "HEITOR DE ALMEIDA HOLANDA", "ISAAC FREITAS DE ARAUJO", "JOSUE GIRAO PAIXAO",
            "LUIS VINICIUS L DE SOUZA", "LUIZ MIGUEL S DOS SANTOS", "MARIA LUIZA LOPES MARTINS",
            "MATHEUS HENRIQUE S LOPES", "NATANAEL AMORIM FERNANDES", "PEDRO LUCCA H RABELO"]
    elif profissional == "Alice":
        beneficiarios_desejados = ["JOAO PEDRO G VASCONCELOS"]
    elif profissional == "Quintina":
        beneficiarios_desejados = ["ANGEL MOURA DE OLIVEIRA", "ERIC DE MEDEIROS CABRAL"]
    elif profissional == "Talya":
        beneficiarios_desejados = ["REBECA ALVES FERREIRA", "FRANCISCO ARTHUR S LIMA"]
    elif profissional == "Wytala":
        beneficiarios_desejados = ["PEDRO LUCCA H RABELO", "JOSUE GIRAO PAIXAO"]
    elif profissional == "Thalya":
        beneficiarios_desejados = ["FRANCISCO ARTHUR S LIMA"]
    elif profissional == "Geane":
        beneficiarios_desejados = ["DAVI PINHEIRO MATIAS"]
    elif profissional == "Olinea":
        beneficiarios_desejados = ["ADRIAN LEVI COSTA AQUINO"]
    elif profissional == "Jaqueline":
        beneficiarios_desejados = ["EMANUELLY MARCELINO LOPES"]
    else:
        beneficiarios_desejados = []  # Caso nenhum profissional corresponda, retorna lista vazia
    
    return beneficiarios_desejados


def obter_beneficiarios_AT():
    # Lista de beneficiários específicos
    beneficiarios_especificos = ["ADRIAN LEVI COSTA AQUINO", "ANGEL MOURA DE OLIVEIRA", "ANTONIO SAULO F ALMEIDA",
                                 "CECILIA PEREIRA MACHADO", "DAVI PINHEIRO MATIAS", "EMANUELLY MARCELINO LOPES",
                                 "ERIC DE MEDEIROS CABRAL", "FRANCISCO ARTHUR S LIMA", "JAMILY COSTA SALDANHA",
                                 "JOAO MIGUEL PARENTE GOMES", "JOAO PEDRO G VASCONCELOS", "JOSUE GIRAO PAIXAO",
                                 "MARIA ISABELLY C SILVA", "MARIA ISABELLY GOMES LIMA", "MARIA LUIZA LOPES MARTINS",
                                 "OSAIAS ALMEIDA CASTRO NT", "PEDRO DE ALMEIDA AVELINO", "PEDRO LUCCA H RABELO",
                                 "REBECA ALVES FERREIRA", "YAN LUCCA LEMOS GOMES", "ARTHUR MIGUEL C QUEIROZ",
                                 "LUIZ GABRIEL O ALVES"]

    return beneficiarios_especificos