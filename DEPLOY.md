# Deploy do Empire Control no Streamlit Cloud

## Passo a Passo

### 1. Criar Repositório no GitHub

1. Acesse https://github.com/new
2. Nome do repositório: `empire-control` (ou outro nome)
3. **IMPORTANTE**: Marque como **Private** (repositório privado)
4. Clique em "Create repository"

### 2. Subir o Código

No terminal (dentro da pasta str1p):

```bash
git init
git add .
git commit -m "Initial commit - Empire Control Dashboard"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/empire-control.git
git push -u origin main
```

Substitua `SEU_USUARIO` pelo seu username do GitHub.

### 3. Deploy no Streamlit Cloud

1. Acesse https://share.streamlit.io/
2. Clique em "New app"
3. Conecte sua conta do GitHub
4. Selecione:
   - Repository: `empire-control`
   - Branch: `main`
   - Main file path: `app.py`
5. Clique em "Deploy"

### 4. Aguarde o Deploy

- Vai levar ~2-5 minutos
- Você verá a URL final: `https://empire-control-XXXXX.streamlit.app`

### 5. Primeiro Acesso

1. Acesse a URL
2. Faça upload dos cookies pela primeira vez
3. Compartilhe a URL com sua companheira

## Atualizações Futuras

Sempre que você quiser atualizar o dashboard:

```bash
git add .
git commit -m "Descrição da mudança"
git push
```

O Streamlit Cloud atualiza automaticamente em ~1 minuto.

## Dados Compartilhados

Os arquivos salvos (cookies, produtos, despesas) ficam no servidor do Streamlit Cloud.
Vocês dois verão os mesmos dados em tempo real.

## Problemas Comuns

**"Repository not found"**
- Verifique se o repositório está público ou se você deu acesso ao Streamlit

**"Module not found"**
- Verifique se o `requirements.txt` está correto

**Cookies não salvam**
- É normal, os dados persistem entre sessões no servidor do Streamlit
