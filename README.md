# Empire Control - Financial Dashboard

Dashboard financeiro centralizado integrando Stipchat API, vendas de estoque e despesas domesticas.

## Instalacao

```bash
pip install -r requirements.txt
```

## Executar

```bash
streamlit run app.py
```

## Configuracao Inicial

### 1. Stipchat API

Para usar a integracao com a API Stipchat, voce precisa obter o Cookie SessionID:

1. Abra `br.stripchat.com` em modo Incognito
2. Faca login na conta
3. Pressione F12 para abrir DevTools
4. Va para: **Application** > **Cookies** > `https://br.stripchat.com`
5. Procure por `stripchat_com_sessionId`
6. Copie o valor do cookie
7. Cole no campo "Cookie SessionID" no sidebar do dashboard

**IMPORTANTE:** O Cookie SessionID expira periodicamente. Se receber erro 403, repita o processo acima para obter um novo cookie.

### 2. Calibracao Financeira

No sidebar, configure:
- **Dolar Hoje (R$):** Cotacao atual do dolar
- **Meta Diaria (R$):** Sua meta de faturamento diario

## Funcionalidades

### Module A: Stipchat API
- Rastreamento em tempo real de tokens e horas online
- Calculo automatico de revenue em BRL
- Comparacao com meta diaria

### Module B: Inventory (Stock)
- Upload de CSV de vendas (SAIDAS.csv)
- Processamento automatico de colunas de moeda brasileira
- Metricas de lucro liquido total

**Formato do CSV:**
- As primeiras 3 linhas sao metadata (puladas automaticamente)
- Colunas de moeda no formato "R$ 1.234,56" sao convertidas automaticamente

### Module C: Household Expenses
- Registro de despesas compartilhadas
- Split automatico 50/50
- Calculo de acerto de contas

### Module D: Executive Dashboard
- Visao consolidada de todas as fontes de receita
- Grand Total: (Stipchat Revenue) + (Stock Profit) - (Total Expenses)
- Graficos e metricas em tempo real

## Estrutura de Arquivos

```
str1p/
├── app.py              # Aplicacao principal
├── requirements.txt    # Dependencias Python
├── despesas.csv        # Dados de despesas (gerado automaticamente)
└── README.md           # Este arquivo
```

## Tecnologias

- **Python 3.10+**
- **Streamlit:** Framework web
- **Pandas:** Manipulacao de dados
- **Plotly:** Visualizacoes interativas
- **Requests:** Chamadas HTTP para API

## Deploy (Streamlit Cloud)

1. Crie repositorio no GitHub com estes arquivos
2. Acesse https://streamlit.io/cloud
3. Conecte seu repositorio
4. Deploy automatico

**Nota:** No Streamlit Cloud, os arquivos CSV serao resetados a cada deploy. Para persistencia permanente, considere integrar com banco de dados.

## Suporte

Para duvidas ou problemas, consulte a documentacao do Streamlit: https://docs.streamlit.io
