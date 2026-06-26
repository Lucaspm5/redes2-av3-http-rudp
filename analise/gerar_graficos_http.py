import matplotlib
matplotlib.use("Agg")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob, os, re

LOG_DIR = '/home/lucas/Redes_2_FINAL/logs'
OUT_DIR = '/home/lucas/Redes_2_FINAL/analise/graficos'
os.makedirs(OUT_DIR, exist_ok=True)

padrao = re.compile(r'fluxo_(tcp|rudp)_([ABC])_(.+)\.csv')
linhas_resumo = []

for caminho in sorted(glob.glob(f'{LOG_DIR}/fluxo_*.csv')):
    nome = os.path.basename(caminho)
    m = padrao.match(nome)
    if not m:
        continue
    protocolo, cenario, arquivo = m.groups()
    colunas = ['exec','tag','caminho','tempo','throughput','bytes']
    if protocolo == 'rudp':
        colunas.append('retransmissoes')
    df = pd.read_csv(caminho, names=colunas)

    media, desvio = df['throughput'].mean(), df['throughput'].std()
    minimo, maximo = df['throughput'].min(), df['throughput'].max()
    tempo_medio = df['tempo'].mean()

    print(f"{protocolo.upper():5s} | {cenario} | {arquivo:20s} | "
          f"media={media:8.4f} Mbps | desvio={desvio:7.4f} | "
          f"tempo_medio={tempo_medio:7.4f}s")

    linhas_resumo.append({
        'protocolo': protocolo.upper(), 'cenario': cenario, 'arquivo': arquivo,
        'media': media, 'desvio': desvio, 'minimo': minimo,
        'maximo': maximo, 'tempo_medio': tempo_medio
    })

resumo = pd.DataFrame(linhas_resumo)
resumo.to_csv(f'{LOG_DIR}/resumo_http.csv', index=False)

cenarios = ['A', 'B', 'C']
for arquivo in resumo['arquivo'].unique():
    sub = resumo[resumo['arquivo'] == arquivo]
    tcp_vals  = [sub[(sub.cenario==c)&(sub.protocolo=='TCP')]['media'].values[0]
                 if len(sub[(sub.cenario==c)&(sub.protocolo=='TCP')]) else 0 for c in cenarios]
    rudp_vals = [sub[(sub.cenario==c)&(sub.protocolo=='RUDP')]['media'].values[0]
                 if len(sub[(sub.cenario==c)&(sub.protocolo=='RUDP')]) else 0 for c in cenarios]

    x, largura = np.arange(len(cenarios)), 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - largura/2, tcp_vals,  largura, label='TCP',   color='steelblue')
    ax.bar(x + largura/2, rudp_vals, largura, label='R-UDP', color='coral')
    ax.set_yscale('log')
    ax.set_xticks(x); ax.set_xticklabels(cenarios)
    ax.set_ylabel('Throughput (Mbps) - escala log')
    ax.set_title(f'HTTP via TCP vs R-UDP — {arquivo}')
    ax.legend(); ax.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(f'{OUT_DIR}/http_{arquivo}.png', dpi=150)
    plt.close()
    print(f"Grafico salvo: http_{arquivo}.png")

print(f"\nTodos os graficos em: {OUT_DIR}")
