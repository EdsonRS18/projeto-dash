# VisMalária: Dashboard de Monitoramento e Análise da Malária no Brasil

Este projeto é uma aplicação web interativa desenvolvida com **Dash** e **Plotly** para a visualização e análise de dados epidemiológicos da malária no Brasil. O foco principal é o monitoramento do **IPA (Índice Parasitário Anual)** e a análise de fluxos de **importação e exportação** de casos entre estados e municípios.

## 🚀 Funcionalidades Principais

- **Monitoramento de IPA**: Mapas coropléticos interativos que mostram o risco de transmissão por estado e município.
- **Análise de Fluxo (Sankey)**: Visualização dos fluxos de infecção, notificação e residência, permitindo identificar as rotas de propagação da doença.
- **Mapas de Conectividade**: Mapas geográficos com conexões (arestas) que mostram a origem e o destino dos casos importados/exportados.
- **Perfil Demográfico**: Pirâmides etárias e de escolaridade por sexo para entender o perfil da população atingida.
- **Canal Endêmico**: Gráfico de corredor epidemiológico (Q1, Mediana, Q3) para comparar os casos atuais com a série histórica e identificar surtos.
- **Filtros Avançados**: Filtragem por ano (2003-2022), estado, município, direção do fluxo e quantidade mínima de notificações.

## 📁 Estrutura do Projeto

```text
app/
├── app.py                # Ponto de entrada da aplicação
├── server.py             # Configuração do servidor Dash e Flask
├── assets/               # Estilos CSS, imagens e ícones
├── callbacks/            # Lógica de interatividade (gráficos e filtros)
│   ├── choropleth_...    # Mapas de incidência (IPA)
│   ├── sankey_...        # Diagramas de fluxo
│   ├── mapa_...          # Mapas de conectividade geográfica
│   └── ...               # Outros componentes (pirâmides, corredor)
├── components/           # Componentes UI reutilizáveis (loading, etc)
├── data/                 # Carregamento de dados e constantes
├── datasets/             # Arquivos CSV com dados históricos
├── domain/               # Regras de negócio e lógica de filtragem
├── geojson/              # Arquivos geográficos para renderização de mapas
├── layouts/              # Definição da estrutura visual (Home, Importada, Exportada)
└── utils/                # Funções auxiliares de visualização
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **Dash**: Framework para construção de interfaces analíticas.
- **Plotly**: Biblioteca de gráficos interativos.
- **Pandas**: Manipulação e análise de dados.
- **Dash Bootstrap Components**: Estilização e componentes responsivos.

## ⚙️ Como Executar

1. Instale as dependências:
   ```bash
   pip install dash dash-bootstrap-components pandas plotly
   ```
2. Navegue até a pasta `app`:
   ```bash
   cd app
   ```
3. Execute a aplicação:
   ```bash
   python app.py
   ```
4. Acesse no navegador: `http://127.0.0.1:8050`

---
*Desenvolvido para auxiliar pesquisadores e gestores de saúde pública no combate à malária.*
