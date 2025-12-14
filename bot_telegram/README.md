# 🤖 Bot Telegram - Guia Completo de Configuração e Execução

## 📋 **VISÃO GERAL**

Este bot Telegram oferece serviços premium com integração ao LivePix para pagamentos PIX. O sistema inclui:

- 🎯 **Serviços Premium**: Vídeos personalizados, chamadas C2C, sexting, packs de fotos
- 💳 **Pagamentos PIX**: Integração completa com LivePix.gg
- 👑 **Grupo VIP**: Acesso automático após pagamento
- 🔧 **Comandos Admin**: Gerenciamento de anúncios e usuários
- 📊 **Sistema de Estados**: Conversas inteligentes e personalizadas

## 🚀 **CONFIGURAÇÃO RÁPIDA**

### **1. Instalar Dependências**
```bash
pip install python-telegram-bot==20.7
pip install requests==2.31.0
```

### **2. Configurar Variáveis de Ambiente**
```bash
python configurar_bot.py
```

### **3. Executar o Bot**
```bash
python executar_bot.py
```

## 🔧 **CONFIGURAÇÃO DETALHADA**

### **Variáveis de Ambiente Necessárias**

Crie um arquivo `.env` com as seguintes configurações:

```env
# Configurações do Bot Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHANNEL_ID=seu_channel_id_aqui
TELEGRAM_ADMIN_ID=seu_admin_id_aqui

# Configurações do LivePix
LIVEPIX_API_KEY=sua_api_key_aqui
LIVEPIX_WEBHOOK_SECRET=seu_webhook_secret_aqui

# Configurações do Bot
BOT_USERNAME=seu_bot_username_aqui
BOT_WEBHOOK_URL=https://seu_dominio.com/webhook
BOT_PORT=8443

# Configurações de Desenvolvimento
DEBUG=true
LOG_LEVEL=INFO
```

### **Como Obter os Tokens**

#### **1. TELEGRAM_BOT_TOKEN**
- Vá para [@BotFather](https://t.me/BotFather) no Telegram
- Digite `/newbot`
- Siga as instruções para criar o bot
- Copie o token fornecido

#### **2. TELEGRAM_CHANNEL_ID**
- Crie um canal no Telegram
- Adicione seu bot como administrador
- Use `@seucanal` ou o ID numérico (ex: `-1001234567890`)

#### **3. TELEGRAM_ADMIN_ID**
- Vá para [@userinfobot](https://t.me/userinfobot) no Telegram
- Digite `/start`
- Copie seu ID numérico

#### **4. LIVEPIX_API_KEY**
- Vá para [livepix.gg](https://livepix.gg)
- Crie uma conta
- Vá em **Configurações > API**
- Copie sua chave de API

#### **5. LIVEPIX_WEBHOOK_SECRET**
- Na mesma página da API do LivePix
- Configure o webhook secret
- Use uma string aleatória segura

## 🧪 **TESTES E VERIFICAÇÃO**

### **Teste de Inicialização**
```bash
python teste_inicializacao.py
```

Este script verifica:
- ✅ Importações funcionando
- ✅ Variáveis de ambiente configuradas
- ✅ Conexão com Telegram
- ✅ Conexão com LivePix

### **Teste de Configuração**
```bash
python configurar_bot.py
```

Este script:
- ✅ Cria arquivo `.env` automaticamente
- ✅ Guia na configuração das variáveis
- ✅ Testa se tudo está configurado corretamente

## 🎮 **EXECUÇÃO DO BOT**

### **Execução Segura**
```bash
python executar_bot.py
```

Este script:
- ✅ Verifica dependências
- ✅ Carrega variáveis de ambiente
- ✅ Valida configuração
- ✅ Executa o bot com segurança

### **Execução Direta**
```bash
python bot.py
```

**⚠️ Certifique-se de que o arquivo `.env` está configurado antes!**

## 📊 **FUNCIONALIDADES DO BOT**

### **Serviços Disponíveis**
- 🎬 **Vídeo Personalizado (6 min)**: R$ 150,00
- 📞 **C2C Chamada (10 min)**: R$ 100,00
- 💬 **Sexting Premium (30 min)**: R$ 300,00
- 📸 **Pack de Fotos (15 pics)**: R$ 120,00
- 💕 **GFE Experience (1 dia)**: R$ 400,00
- 🍆 **Avaliação de Dick**: R$ 20,00

### **Comandos Disponíveis**
- `/start` - Inicia o bot
- `/menu` - Mostra menu principal
- `/help` - Ajuda e informações
- `/admin` - Comandos administrativos (apenas admins)

### **Sistema de Pagamentos**
- 💳 **PIX**: Integração completa com LivePix
- 🔒 **Seguro**: Processamento seguro de pagamentos
- ⚡ **Automático**: Acesso automático após confirmação
- 📱 **Notificações**: Status de pagamento em tempo real

## 🔧 **COMANDOS ADMINISTRATIVOS**

### **Comandos Disponíveis**
- `/admin` - Menu administrativo
- `/announce` - Criar anúncio no canal
- `/stats` - Estatísticas do bot
- `/users` - Lista de usuários
- `/payments` - Histórico de pagamentos

### **Permissões**
- Apenas usuários com `TELEGRAM_ADMIN_ID` podem usar comandos admin
- Acesso completo ao sistema de anúncios
- Monitoramento de pagamentos e usuários

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Erro: "TELEGRAM_BOT_TOKEN não definida"**
```bash
# Verifique se o arquivo .env existe
ls -la .env

# Configure as variáveis
python configurar_bot.py
```

### **Erro: "python-telegram-bot não instalado"**
```bash
pip install python-telegram-bot==20.7
```

### **Erro: "Conexão com Telegram falhou"**
- Verifique se o token está correto
- Confirme se o bot está ativo
- Teste a conexão com `python teste_inicializacao.py`

### **Erro: "Conexão com LivePix falhou"**
- Verifique se a API key está correta
- Confirme se a conta LivePix está ativa
- Teste a conexão com `python teste_inicializacao.py`

### **Bot não responde**
- Verifique se está executando: `python executar_bot.py`
- Confirme se o bot está online no Telegram
- Verifique os logs para erros

## 📁 **ESTRUTURA DO PROJETO**

```
bot_telegram/
├── bot.py                    # Código principal do bot
├── requirements.txt          # Dependências Python
├── configurar_bot.py         # Script de configuração
├── executar_bot.py          # Script de execução segura
├── teste_inicializacao.py   # Testes de inicialização
├── .env.example             # Exemplo de configuração
├── .env                     # Suas configurações (criado automaticamente)
└── README.md                # Este arquivo
```

## 🔄 **ATUALIZAÇÕES E MANUTENÇÃO**

### **Atualizar Dependências**
```bash
pip install --upgrade python-telegram-bot requests
```

### **Backup das Configurações**
```bash
cp .env .env.backup
```

### **Logs e Monitoramento**
- O bot gera logs automáticos
- Monitore o console para erros
- Use `DEBUG=true` no `.env` para logs detalhados

## 🎯 **PRÓXIMOS PASSOS**

Após configurar e executar o bot:

1. **Teste os Serviços**: Verifique se todos os serviços estão funcionando
2. **Configure Webhooks**: Configure webhooks do LivePix se necessário
3. **Monitore Pagamentos**: Acompanhe os pagamentos no painel LivePix
4. **Personalize Mensagens**: Ajuste as mensagens conforme necessário
5. **Adicione Funcionalidades**: Expanda o bot com novas funcionalidades

## 🆘 **SUPORTE**

Se encontrar problemas:

1. **Execute o teste**: `python teste_inicializacao.py`
2. **Verifique a configuração**: `python configurar_bot.py`
3. **Consulte os logs**: Verifique mensagens de erro no console
4. **Teste as conexões**: Verifique Telegram e LivePix separadamente

## 🎉 **SUCESSO!**

Se tudo estiver configurado corretamente, você verá:

```
✅ Bot conectado: @seubot
✅ LivePix API conectada com sucesso
✅ Todas as variáveis estão configuradas
✅ Bot pronto para ser executado
```

**🚀 Seu bot Telegram está pronto para funcionar!**
