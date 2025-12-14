# Empire Control

Financial Command Center - Dashboard para controle financeiro pessoal integrado.

## Funcionalidades

### 💰 Revenue Tracking
- Rastreamento de receitas via API
- Análise de sessões e performance
- Métricas e metas configuráveis

### 📦 Inventory Management
- Gestão completa de produtos
- Controle de estoque em gramas
- Registro de vendas parciais
- Cálculo automático de lucro

### 🏠 Household Expenses
- Registro de despesas compartilhadas
- Split automático 50/50
- Cálculo de acertos

### 📊 Executive Dashboard
- Visão consolidada de receitas
- Gráficos e analytics em tempo real
- KPIs personalizados

## Tecnologias

- Python 3.10+
- Streamlit
- Pandas
- Plotly
- Requests

## Instalação Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configuração

1. Acesse o dashboard
2. Faça upload dos cookies de autenticação (primeira vez)
3. Configure produtos no módulo Inventory
4. Registre despesas conforme necessário

## Deploy no Streamlit Cloud

Ver arquivo `DEPLOY.md` para instruções completas.

## Estrutura de Arquivos

```
str1p/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências Python
├── produtos.json       # Dados de produtos (gerado automaticamente)
├── vendas.json         # Histórico de vendas
├── despesas.csv        # Registro de despesas
└── README.md           # Este arquivo
```

## Segurança

- Todos os dados sensíveis estão no `.gitignore`
- Cookies e informações financeiras não são versionados
- Use repositório privado para deploy em produção

## Suporte

Para dúvidas sobre Streamlit: https://docs.streamlit.io
