import matplotlib
matplotlib.use('Agg')

import pandas as pd
import mplfinance as mpf
import os
from datetime import datetime, timedelta

ARQUIVO_CSV = 'WDOFUT_formatado_corrigido.csv'
DIRETORIO_BASE = 'dataset_2_WDO_M15_512x512'

def gerar_dataset_de_csv():
    print(f"Iniciando processamento do arquivo: {ARQUIVO_CSV}")

    try:
        dados_completos = pd.read_csv(ARQUIVO_CSV, sep='\t', header=0)
        print("Arquivo CSV carregado com sucesso.")

        mapa_renomear = {
            '<OPEN>': 'Open',
            '<HIGH>': 'High',
            '<LOW>': 'Low',
            '<CLOSE>': 'Close',
            '<TICKVOL>': 'Volume'
        }
        dados_completos.rename(columns=mapa_renomear, inplace=True)

        dados_completos['datetime'] = pd.to_datetime(
            dados_completos['<DATE>'] + ' ' + dados_completos['<TIME>']
        )
        dados_completos.set_index('datetime', inplace=True)

        # 🌟 Cálculo das médias móveis
        dados_completos['MM5'] = dados_completos['Close'].rolling(5).mean()
        dados_completos['MM20'] = dados_completos['Close'].rolling(20).mean()
        dados_completos['MM50'] = dados_completos['Close'].rolling(50).mean()
        dados_completos['MM100'] = dados_completos['Close'].rolling(100).mean()

        print("Médias móveis calculadas.")

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

                    # 🌟 Médias móveis adicionadas ao plot
                    add_plots = [
                        mpf.make_addplot(dados_dia['MM5'], color='blue', width=0.7),
                        mpf.make_addplot(dados_dia['MM20'], color='orange', width=0.7),
                        mpf.make_addplot(dados_dia['MM50'], color='purple', width=0.7),
                        mpf.make_addplot(dados_dia['MM100'], color='green', width=0.7),
                    ]

                    # 🌟 Gerar plot com horário
                    mpf.plot(
                        dados_dia,
                        type='candle',
                        style='yahoo',
                        volume=True,
                        figsize=(5.12, 5.12),
                        addplot=add_plots,
                        xrotation=90,  # mostra os horários
                        savefig=dict(fname=caminho_completo, dpi=100, pad_inches=0)
                    )

                    print(f"  -> Gráfico salvo em: {caminho_completo}")

            except KeyError:
                print(f"  -> Sem dados para {start_str}.")
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
