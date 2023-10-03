from models import db, Beneficiario, Producao, DadosProducao, Profissional, ResumoProducao
import pandas as pd


# Lista de nomes de profissionais
nomes_profissionais = [
    "Alice", "Darlene", "Davylla", "Elizza", "Gabriela",
    "Geane", "Ivana", "Jaqueline", "Jayanne", "Joana",
    "Jô", "Mariana", "Mariane", "Olinea", "Quintina",
    "Simone", "Thalia", "Wytalla"
]

# Caso altere o nome da Darlene na lista acima, precisa lembrar de alterar também no método abaixo criar_beneficiarios_do_dataframe

def criar_beneficiarios_do_dataframe(df, beneficiarios_AT):
    
    atendente1 = Profissional.query.filter_by(nome="Darlene")

    primeiro_atendente = atendente1.first()

    for index, row in df.iterrows():
        nome = row['Beneficiário']

        # Verifica se já existe um beneficiário com o mesmo nome
        beneficiario_existente = Beneficiario.query.filter_by(nome=nome).first()
        tipo = ""
        if beneficiario_existente is None:
                
            if nome in beneficiarios_AT:
                tipo = "AT"
            else:
                tipo = "Clínica"
            novo_beneficiario = Beneficiario(nome=nome, tipo=tipo, atendente_1_id=primeiro_atendente.id)
            db.session.add(novo_beneficiario)
        
        # novo_beneficiario = Beneficiario(nome=nome)
        # db.session.add(novo_beneficiario)
    
    db.session.commit()


# def criar_nova_producao(df, producao_movimetacao):
#     # Criar a nova produção apenas se não existir
#                     nova_producao = Producao(producao_movimetacao=producao_movimetacao)
#                     db.session.add(nova_producao)
#                     db.session.commit()

#                     # Supondo que você tenha um DataFrame "dados" com os dados a serem adicionados à tabela "DadosProducao"
#                     dados = df

#                     # Convert 'Qtd.Paga' and 'Valor' columns to numeric types
#                     dados['Qtd.Paga'] = dados['Qtd.Paga'].str.replace(',', '.').astype(float)
#                     dados['Valor'] = dados['Valor'].str.replace(',', '.').astype(float)

#                     # Convert 'Data-Hora' to datetime format
#                     dados['Data-Hora'] = pd.to_datetime(dados['Data-Hora'], format='%d/%m/%Y %H:%M:%S')                    

#                     for _, row in dados.iterrows():
#                         nova_dados_producao = DadosProducao(
#                             lote=row['Lote'],
#                             data_hora=pd.to_datetime(row['Data-Hora']),
#                             codigo=row['Código'],
#                             beneficiario=row['Beneficiário'],
#                             qtd_paga=row['Qtd.Paga'],
#                             valor=row['Valor'],
#                             producao_id=nova_producao.id  # Associar a linha de dados à produção recém-criada
#                         ) #  Lote,  Data-Hora , Código,  Beneficiario,  Qtd.Paga  e  Valor
#                         db.session.add(nova_dados_producao)
                    
#                     db.session.commit()

def criar_nova_producao(df, producao_movimetacao):
    # Criar a nova produção apenas se não existir
    nova_producao = Producao.query.filter_by(producao_movimetacao=producao_movimetacao).first()
    
    if nova_producao is None:
        nova_producao = Producao(producao_movimetacao=producao_movimetacao)
        db.session.add(nova_producao)
        db.session.commit()

    dados = df
    dados['Qtd.Paga'] = dados['Qtd.Paga'].str.replace(',', '.').astype(float)
    dados['Valor'] = dados['Valor'].str.replace(',', '.').astype(float)
    dados['Data-Hora'] = pd.to_datetime(dados['Data-Hora'], format='%d/%m/%Y %H:%M:%S')

    for _, row in dados.iterrows():
        nome_beneficiario = row['Beneficiário']
        beneficiario = Beneficiario.query.filter_by(nome=nome_beneficiario).first()

        if beneficiario is None:
            continue

        nova_dados_producao = DadosProducao(
            lote=row['Lote'],
            data_hora=row['Data-Hora'],
            codigo=row['Código'],
            beneficiario_id=beneficiario.id,  # Usar o ID do beneficiário
            qtd_paga=row['Qtd.Paga'],
            valor=row['Valor'],
            producao_id=nova_producao.id
        )
        db.session.add(nova_dados_producao)

    db.session.commit()



def adicionar_profissionais():
    for nome in nomes_profissionais:
        profissional_existente = Profissional.query.filter_by(nome=nome).first()
        if not profissional_existente:
            profissional = Profissional(nome=nome)
            db.session.add(profissional)
    db.session.commit()

# Função para criar a nova tabela a partir dos dados existentes
def criar_resumo_producao():
    # Consulta para obter os dados da tabela DadosProducao onde o código seja igual a '500510'
    dados = DadosProducao.query.filter_by(codigo='5000510').all()

    # Dicionário para armazenar os dados agregados por beneficiario_id e producao_id
    dados_agregados = {}

    # Loop pelos dados e agregação
    for dado in dados:
        chave = (dado.beneficiario_id, dado.producao_id)
        if chave not in dados_agregados:
            dados_agregados[chave] = 0
        dados_agregados[chave] += dado.qtd_paga

    # Inserir os dados agregados na nova tabela
    for chave, qtd_total in dados_agregados.items():
        beneficiario_id, producao_id = chave
        nova_linha = ResumoProducao(beneficiario_id=beneficiario_id, qtd_total=qtd_total, producao_id=producao_id)
        db.session.add(nova_linha)

    # Commit das alterações
    db.session.commit()

