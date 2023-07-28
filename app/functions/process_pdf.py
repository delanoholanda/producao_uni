
import re
import PyPDF2


def extrairTextoPdf(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as arquivo:
        leitor_pdf = PyPDF2.PdfReader(arquivo)
        num_paginas = len(leitor_pdf.pages)
        linha_producao_movimento = ""

        texto_completo = 'Lote Nota Data Beneficiário Total Código Qt. Cobr Qt. Paga Valor Qtd CH Subtotal\n'
        padrao_pagina = re.compile(r'Página:\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}Modelo Completo')
        padrao_texto_adicional = re.compile(r'\d+Data de Emissão:.*?SERTAO CENTRAL', re.DOTALL)
        padrao_cabecalho = re.compile(r'Lote Nota Data Beneficiário Código Qt\. Cobr Qt\. Paga Valor Qtd CH Subtotal Total Nota', re.DOTALL)


        # Recupera do PDF o número da Produção e Movimentação
        for pagina in range(0,1):
            pagina_pdf = leitor_pdf.pages[pagina]
            texto = pagina_pdf.extract_text()

            # Find the line containing the pattern "2023/6/97-Q"
            pattern = r"\d{4}/\d/\d{1,3}-[A-Z]{1}"
            linha_producao_movimento = re.search(pattern, texto)
            if linha_producao_movimento:
               continue 
            else:    
                return "", linha_producao_movimento

            # if linha_producao_movimento:
            #     print(linha_producao_movimento.group())
            # else:
            #     print("Pattern not found.")


        for pagina in range(num_paginas):
            pagina_pdf = leitor_pdf.pages[pagina]
            texto = pagina_pdf.extract_text()


            # # Find the line containing the pattern "2023/6/97-Q"
            # padtaProducaoMovimento = r"\d{4}/\d/\d{1,3}-[A-Z]{1}"
            # linha_producao_movimento = re.search(padtaProducaoMovimento, texto)
            # print("aquiiii")
            # print(linha_producao_movimento)
            
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

        

        return texto_completo.strip(), linha_producao_movimento # Remover espaços em branco extras no início e no final do texto
    
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

