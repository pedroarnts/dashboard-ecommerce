# Dashboard de produtos de e-commerce

Este projeto parte de uma base com 295 produtos de e-commerce e tenta responder algumas perguntas simples: como os preços se distribuem, se o desconto tem a ver com o preço, se produtos mais avaliados vendem mais e quais marcas aparecem com mais frequência.

Para que qualquer pessoa consiga explorar os dados pelo navegador, sem precisar abrir o Python nem mexer em código, os gráficos ficam reunidos em um dashboard feito com Dash.

## Arquivos

- `app.py`: o dashboard
- `requirements.txt`: as bibliotecas que o dashboard usa
- `ecommerce_estatistica.csv`: a base de dados

## O que o dashboard mostra

Sete gráficos na mesma página:

1. Histograma dos preços, com a média e a mediana marcadas
2. Dispersão entre preço e desconto
3. Mapa de calor com a correlação entre as variáveis numéricas
4. Ranking das marcas com mais produtos
5. Pizza com a divisão por gênero
6. Densidade dos preços de produtos masculinos e femininos
7. Regressão entre número de avaliações e quantidade vendida (em escala logarítmica)

Há três filtros no topo da página, e qualquer mudança neles atualiza todos os gráficos de uma vez: a faixa de preço, o gênero (masculino, feminino ou outros) e o tamanho do ranking de marcas (5, 10, 15 ou 20). Logo abaixo dos filtros aparece um resumo com o número de produtos selecionados, o preço médio e o desconto médio. Se a combinação de filtros não deixar nenhum produto, os gráficos avisam isso em vez de quebrar.

## Como rodar

Precisa do Python instalado. Na pasta do projeto:

```
pip install -r requirements.txt
python app.py
```

Depois é só abrir http://127.0.0.1:8050 no navegador. O arquivo CSV precisa estar na mesma pasta do `app.py`.

## Como colocar no ar

O `app.py` já deixa a variável `server` disponível, então dá para publicar em serviços como o Render ou similares. O comando de inicialização é:

```
gunicorn app:server
```

O serviço entrega um link, e quem receber o link abre o dashboard direto no navegador.

## O que a análise mostrou

- A maior parte dos produtos custa entre R$ 50 e R$ 200. Os preços formam dois grupos, um perto de R$ 60 e outro perto de R$ 130.
- O desconto praticamente não depende do preço: a correlação é de cerca de 0,16.
- Produtos com mais avaliações vendem mais (correlação de cerca de 0,91). Isso indica que as duas coisas caminham juntas, mas não prova que uma causa a outra.
- A Lupo é a marca com mais produtos no catálogo.
- Os produtos masculinos são mais caros em média: cerca de R$ 155, contra R$ 105 dos femininos.

Ferramentas usadas: Python, pandas, numpy, Plotly e Dash.
