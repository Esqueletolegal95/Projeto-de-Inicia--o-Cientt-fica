import matplotlib
# Força o uso de um backend não-interativo para evitar erros de GUI no Linux
matplotlib.use('Agg')

import pandas as pd
import mplfinance as mpf
import os
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---

# Nome do arquivo CSV que você enviou.
ARQUIVO_CSV = 'WDO$N_M15_201811260900_202311231815.csv' 

# Diretório base para salvar as imagens
DIRETORIO_BASE = 'dataset_WDO_M15_512x512'

# --- FIM DAS CONFIGURAÇÕES ---

def gerar_dataset_de_csv():
    """
    Lê um arquivo CSV do MT5, processa os dados e gera imagens de candlestick
    para cada dia no formato 512x512, otimizadas para treinamento de IA.
    """
    print(f"Iniciando processamento do arquivo: {ARQUIVO_CSV}")

    try:
        dados_completos = pd.read_csv(ARQUIVO_CSV, sep='\t', header=0)
        print("Arquivo CSV carregado com sucesso.")

        # --- PREPARAÇÃO DOS DADOS ---
        mapa_renomear = {
            '<OPEN>': 'Open',
            '<HIGH>': 'High',
            '<LOW>': 'Low',
            '<CLOSE>': 'Close',
            '<TICKVOL>': 'Volume'
        }
        dados_completos.rename(columns=mapa_renomear, inplace=True)
        dados_completos['datetime'] = pd.to_datetime(dados_completos['<DATE>'] + ' ' + dados_completos['<TIME>'])
        dados_completos.set_index('datetime', inplace=True)
        print("Dados preparados para processamento.")

        # --- GERAÇÃO DAS IMAGENS ---
        data_inicio = dados_completos.index.min().date()
        data_fim = dados_completos.index.max().date()
        print(f"Período dos dados: de {data_inicio} a {data_fim}")

        data_atual = data_inicio
        while data_atual <= data_fim:
            start_str = data_atual.strftime('%Y-%m-%d')
            print(f"Processando dia: {start_str}...")

            try:
                dados_dia = dados_completos.loc[start_str]
                if not dados_dia.empty:
                    ano = str(data_atual.year)
                    mes = f"{data_atual.month:02d}"
                    caminho_salvar = os.path.join(DIRETORIO_BASE, ano, mes)
                    os.makedirs(caminho_salvar, exist_ok=True)

                    nome_arquivo = f"{start_str}_WDO_M15_512x512.png"
                    caminho_completo = os.path.join(caminho_salvar, nome_arquivo)

                    # --- CONFIGURAÇÃO DO PLOT PARA IA ---
                    mpf.plot(
                        dados_dia,
                        type='candle',
                        style='yahoo',
                        volume=True,
                        # --- Alterações para o formato 512x512 ---
                        figsize=(5.12, 5.12), # Tamanho da figura em polegadas (512 pixels / 100 dpi)
                        axisoff=True, # Remove todos os eixos (preço, tempo, etc.)
                        savefig=dict(fname=caminho_completo, dpi=100, pad_inches=0) # Salva com 100 dpi e sem preenchimento
                    )
                    print(f"  -> Gráfico salvo em: {caminho_completo}")

            except KeyError:
                 print(f"  -> Sem dados para {start_str} (dia não encontrado no índice).")
            except Exception as e:
                print(f"  -> Erro ao gerar o gráfico para {start_str}: {e}")
            
            data_atual += timedelta(days=1)

    except FileNotFoundError:
        print(f"ERRO: O arquivo '{ARQUIVO_CSV}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

    print("\nProcesso concluído!")

if __name__ == '__main__':
    gerar_dataset_de_csv()