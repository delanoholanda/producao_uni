from models import db, Beneficiario, Producao, DadosProducao
import pandas as pd

def criar_beneficiarios_do_dataframe(df, beneficiarios_AT):
    for index, row in df.iterrows():
        nome = row['Beneficiário']

        # Verifica se já existe um beneficiário com o mesmo nome
        beneficiario_existente = Beneficiario.query.filter_by(nome=nome).first()
        tipo = ""
        if beneficiario_existente is None:
                
            if nome in beneficiarios_AT:
                tipo = "AT"
            else:
                tipo = "Clinica"
            novo_beneficiario = Beneficiario(nome=nome, tipo=tipo)
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