"""Reúne os 7 gráficos do módulo anterior em um dashboard interativo.
Para rodar:  python app.py   e abrir  http://127.0.0.1:8050
"""
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

# ---------------------------------------------------------------- dados
df = pd.read_csv("ecommerce_estatistica.csv")

COLUNAS_NUM = ["Nota", "N_Avaliações", "Desconto", "Preço", "Qtd_Vendidos_Cod"]

# Gênero: mantém Masculino/Feminino e agrupa o resto em "Outros"
df["Gênero_grupo"] = df["Gênero"].where(df["Gênero"].isin(["Masculino", "Feminino"]), "Outros")

PRECO_MIN = float(np.floor(df["Preço"].min()))
PRECO_MAX = float(np.ceil(df["Preço"].max()))
GENEROS = ["Masculino", "Feminino", "Outros"]
CORES_GENERO = {"Masculino": "#4C72B0", "Feminino": "#DD8452", "Outros": "#8C8C8C"}


def filtrar(faixa_preco, generos):
    """Aplica os filtros de preço e gênero ao DataFrame."""
    dados = df[df["Preço"].between(faixa_preco[0], faixa_preco[1])]
    if generos:
        dados = dados[dados["Gênero_grupo"].isin(generos)]
    else:
        dados = dados.iloc[0:0]
    return dados


def figura_vazia(titulo):
    fig = px.scatter(title=titulo)
    fig.add_annotation(text="Nenhum produto com os filtros selecionados",
                       showarrow=False, font={"size": 14})
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


# ---------------------------------------------------------------- gráficos
def grafico_histograma(d):
    if d.empty:
        return figura_vazia("Distribuição dos Preços dos Produtos")
    fig = px.histogram(d, x="Preço", nbins=20, color_discrete_sequence=["#4C72B0"])
    fig.add_vline(x=d["Preço"].mean(), line_dash="dash", line_color="red",
                  annotation_text=f"Média: R$ {d['Preço'].mean():.2f}",
                  annotation_position="top right")
    fig.add_vline(x=d["Preço"].median(), line_dash="dash", line_color="green",
                  annotation_text=f"Mediana: R$ {d['Preço'].median():.2f}",
                  annotation_position="top left")
    fig.update_layout(title="Distribuição dos Preços dos Produtos",
                      xaxis_title="Preço (R$)", yaxis_title="Quantidade de produtos")
    return fig


def grafico_dispersao(d):
    if d.empty:
        return figura_vazia("Relação entre Preço e Desconto")
    fig = px.scatter(d, x="Preço", y="Desconto", opacity=0.6, hover_name="Título",
                     color_discrete_sequence=["#DD8452"])
    fig.update_layout(title="Relação entre Preço e Desconto",
                      xaxis_title="Preço (R$)", yaxis_title="Desconto (%)")
    return fig


def grafico_mapa_calor(d):
    if len(d) < 3:
        return figura_vazia("Mapa de Calor — Correlação entre Variáveis Numéricas")
    corr = d[COLUNAS_NUM].corr().round(2)
    fig = px.imshow(corr, text_auto=True, aspect="auto", zmin=-1, zmax=1,
                    color_continuous_scale="RdBu_r")
    fig.update_layout(title="Mapa de Calor — Correlação entre Variáveis Numéricas")
    return fig


def grafico_barras(d, top_n):
    if d.empty:
        return figura_vazia(f"Top {top_n} Marcas por Quantidade de Produtos")
    top = d["Marca"].value_counts().head(top_n).sort_values()
    fig = px.bar(x=top.values, y=top.index, orientation="h",
                 color_discrete_sequence=["#55A868"])
    fig.update_layout(title=f"Top {top_n} Marcas por Quantidade de Produtos",
                      xaxis_title="Quantidade de produtos", yaxis_title="Marca")
    return fig


def grafico_pizza(d):
    if d.empty:
        return figura_vazia("Distribuição dos Produtos por Gênero")
    cont = d["Gênero_grupo"].value_counts().reset_index()
    cont.columns = ["Gênero", "Quantidade"]
    fig = px.pie(cont, names="Gênero", values="Quantidade", color="Gênero",
                 color_discrete_map=CORES_GENERO)
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(title="Distribuição dos Produtos por Gênero")
    return fig


def grafico_densidade(d):
    """Densidade de preço por gênero (KDE calculado com numpy, sem scipy)."""
    titulo = "Densidade dos Preços — Masculino × Feminino"
    d = d[d["Gênero_grupo"].isin(["Masculino", "Feminino"])]
    if d.empty:
        return figura_vazia(titulo)
    xs = np.linspace(PRECO_MIN - 40, PRECO_MAX + 40, 300)
    fig = px.line()
    for genero in ["Masculino", "Feminino"]:
        precos = d.loc[d["Gênero_grupo"] == genero, "Preço"].to_numpy()
        if len(precos) < 2:
            continue
        h = 1.06 * precos.std(ddof=1) * len(precos) ** (-1 / 5)  # regra de Silverman
        h = max(h, 1e-6)
        dens = np.exp(-0.5 * ((xs[:, None] - precos[None, :]) / h) ** 2).sum(axis=1)
        dens /= len(precos) * h * np.sqrt(2 * np.pi)
        fig.add_scatter(x=xs, y=dens, mode="lines", name=genero, fill="tozeroy",
                        line={"color": CORES_GENERO[genero]},
                        opacity=0.6)
    fig.update_layout(title=titulo, xaxis_title="Preço (R$)", yaxis_title="Densidade")
    return fig


def grafico_regressao(d):
    titulo = "Regressão: Número de Avaliações × Quantidade Vendida (escala log)"
    if len(d) < 3:
        return figura_vazia(titulo)
    dados = pd.DataFrame({
        "log_avaliacoes": np.log10(d["N_Avaliações"]),
        "log_vendas": np.log10(d["Qtd_Vendidos_Cod"]),
        "Título": d["Título"],
    })
    fig = px.scatter(dados, x="log_avaliacoes", y="log_vendas", opacity=0.5,
                     hover_name="Título")
    # reta de regressão (mínimos quadrados) calculada com numpy
    a, b = np.polyfit(dados["log_avaliacoes"], dados["log_vendas"], 1)
    x_reta = np.array([dados["log_avaliacoes"].min(), dados["log_avaliacoes"].max()])
    fig.add_scatter(x=x_reta, y=a * x_reta + b, mode="lines", name="Regressão",
                    line={"color": "red"})
    fig.update_layout(title=titulo, xaxis_title="Número de avaliações (log10)",
                      yaxis_title="Quantidade vendida (log10)", showlegend=False)
    return fig


# ---------------------------------------------------------------- layout
ESTILO_CARD = {"background": "white", "borderRadius": "8px", "padding": "8px",
               "boxShadow": "0 1px 4px rgba(0,0,0,0.15)"}


def card_grafico(id_grafico, legenda):
    return html.Div([
        dcc.Graph(id=id_grafico),
        html.P(legenda, style={"fontSize": "13px", "color": "#555", "margin": "0 8px 8px"}),
    ], style=ESTILO_CARD)


def cria_app():
    app = Dash(__name__)
    app.title = "Análise de E-commerce"

    app.layout = html.Div([
        html.H1("Dashboard — Análise de Produtos de E-commerce"),
        html.P("Explore preços, descontos, avaliações e vendas. "
               "Os filtros abaixo atualizam todos os gráficos."),

        html.Div([
            html.Div([
                html.Label("Faixa de preço (R$)"),
                dcc.RangeSlider(id="filtro-preco", min=PRECO_MIN, max=PRECO_MAX, step=5,
                                value=[PRECO_MIN, PRECO_MAX],
                                marks={int(v): f"{int(v)}" for v in
                                       np.linspace(PRECO_MIN, PRECO_MAX, 6)},
                                tooltip={"placement": "bottom"}),
            ], style={"flex": "2", "minWidth": "280px", "padding": "0 16px"}),
            html.Div([
                html.Label("Gênero"),
                dcc.Checklist(id="filtro-genero", options=GENEROS, value=GENEROS,
                              inline=True, inputStyle={"marginLeft": "12px",
                                                       "marginRight": "4px"}),
            ], style={"flex": "1", "minWidth": "240px"}),
            html.Div([
                html.Label("Marcas no ranking"),
                dcc.Dropdown(id="filtro-top", options=[5, 10, 15, 20], value=10,
                             clearable=False),
            ], style={"flex": "1", "minWidth": "140px"}),
        ], style={**ESTILO_CARD, "display": "flex", "gap": "16px",
                  "alignItems": "center", "marginBottom": "16px", "padding": "16px"}),

        html.Div(id="resumo", style={"marginBottom": "16px", "fontWeight": "bold"}),

        html.Div([
            card_grafico("g-histograma",
                         "A maioria dos produtos custa entre R$ 50 e R$ 200."),
            card_grafico("g-dispersao",
                         "Quase não há relação entre preço e desconto."),
            card_grafico("g-mapa-calor",
                         "Avaliações e vendas andam juntas (correlação forte)."),
            card_grafico("g-barras", "Marcas com mais produtos no catálogo."),
            card_grafico("g-pizza", "Divisão do catálogo por gênero."),
            card_grafico("g-densidade",
                         "Produtos masculinos tendem a ter preço médio maior."),
            card_grafico("g-regressao",
                         "Mais avaliações, mais vendas — uma associação, não causalidade."),
        ], style={"display": "grid",
                  "gridTemplateColumns": "repeat(auto-fit, minmax(480px, 1fr))",
                  "gap": "16px"}),
    ], style={"fontFamily": "Arial, sans-serif", "padding": "24px",
              "background": "#f3f4f6", "maxWidth": "1500px", "margin": "0 auto"})

    @app.callback(
        Output("resumo", "children"),
        Output("g-histograma", "figure"),
        Output("g-dispersao", "figure"),
        Output("g-mapa-calor", "figure"),
        Output("g-barras", "figure"),
        Output("g-pizza", "figure"),
        Output("g-densidade", "figure"),
        Output("g-regressao", "figure"),
        Input("filtro-preco", "value"),
        Input("filtro-genero", "value"),
        Input("filtro-top", "value"),
    )
    def atualiza(faixa_preco, generos, top_n):
        d = filtrar(faixa_preco, generos)
        resumo = f"{len(d)} de {len(df)} produtos selecionados"
        if not d.empty:
            resumo += (f" | preço médio: R$ {d['Preço'].mean():.2f}"
                       f" | desconto médio: {d['Desconto'].mean():.1f}%")
        return (resumo,
                grafico_histograma(d),
                grafico_dispersao(d),
                grafico_mapa_calor(d),
                grafico_barras(d, top_n),
                grafico_pizza(d),
                grafico_densidade(d),
                grafico_regressao(d))

    return app


app = cria_app()
server = app.server  # permite publicar com gunicorn (ex.: Render)

if __name__ == "__main__":
    app.run(debug=True, port=8050)
