# 📹 Sistema de Catálogo de Conteúdos - GirlfrienDine Bot

## 🎯 **VISÃO GERAL**

Sistema completo para venda de vídeos e fotos pré-gravados diretamente pelo bot, com:
- ✅ Catálogo organizado por categorias
- ✅ Preview de conteúdos
- ✅ Pagamento via PIX (LivePix.gg)
- ✅ Entrega automática após confirmação
- ✅ Dashboard web para análises
- ✅ Notificações para admin

---

## 📁 **ARQUIVOS CRIADOS**

### **Backend/Lógica:**
1. `catalog_system.py` - Sistema de persistência e gerenciamento do catálogo
2. `bot_catalog_integration.py` - Integração do catálogo com o bot (menus, compras, entregas)
3. `bot_catalog_admin.py` - Comandos administrativos para gerenciar catálogo

### **Dashboard Web:**
4. `dashboard.py` - Servidor Flask para dashboard administrativo
5. `templates/base.html` - Template base do dashboard
6. `templates/login.html` - Tela de login
7. `templates/index.html` - Dashboard principal (visão geral)

### **Dados:**
- `catalog_data.json` - Banco de dados do catálogo (criado automaticamente)
- `purchases_data.json` - Histórico de compras (criado automaticamente)

---

## 🚀 **COMO USAR**

### **1️⃣ Instalar Dependências**

```bash
pip install -r requirements.txt
```

### **2️⃣ Iniciar o Bot**

O bot já está configurado para usar o catálogo. Basta iniciar normalmente:

```bash
python bot.py
```

### **3️⃣ Iniciar o Dashboard (Opcional)**

Em outro terminal:

```bash
python dashboard.py
```

Acesse: `http://localhost:5000`
- **Senha padrão:** `DinaGostosa2025!` (pode ser alterada em `dashboard.py` ou via variável de ambiente `DASHBOARD_PASSWORD`)

---

## 📝 **COMANDOS ADMIN - GERENCIAR CATÁLOGO**

### **Adicionar Conteúdo:**
```
/addcontent
```
1. Bot pede para enviar o vídeo/fotos
2. Envie o arquivo completo
3. Envie uma preview (GIF ou foto)
4. Envie os detalhes no formato:
   ```
   Título do Conteúdo
   Descrição detalhada
   Categoria (solo/duo/fetiche/personalizados/outros)
   Preço (apenas número, ex: 50)
   Duração (ex: 5 min) ou Quantidade (ex: 10)
   ```

**Exemplo:**
```
Strip Tease Sensual
Vídeo de strip tease com lingerie vermelha
solo
50
5 min
```

### **Listar Catálogo:**
```
/listcatalog
```
Mostra todos os conteúdos do catálogo com IDs.

### **Remover Conteúdo:**
```
/removecontent <content_id>
```
**Exemplo:** `/removecontent content_20251020123456`

### **Estatísticas:**
```
/catalogstats
```
Mostra estatísticas de vendas e catálogo.

---

## 👤 **PARA USUÁRIOS - COMO COMPRAR**

1. Usuário clica em "📹 Catálogo" no menu principal
2. Escolhe uma categoria (Solo, Duo, Fetiche, etc.)
3. Vê lista de conteúdos disponíveis
4. Clica em um conteúdo para ver detalhes e preview
5. Clica em "💳 Comprar Agora"
6. Recebe link do PIX para pagamento
7. **Após pagar, o conteúdo é entregue automaticamente!**

---

## 📊 **DASHBOARD WEB**

### **Funcionalidades:**
- 📈 **Visão Geral:** Estatísticas de vendas, receita, conteúdos
- 📹 **Catálogo:** Visualizar todos os conteúdos por categoria
- 💰 **Vendas:** Histórico completo de compras
- 📊 **Análises:** Gráficos de receita diária e vendas por categoria

### **Acesso:**
1. Inicie o dashboard: `python dashboard.py`
2. Acesse: `http://localhost:5000`
3. Login com senha: `DinaGostosa2025!`

---

## ⚙️ **ESTRUTURA DOS DADOS**

### **Catálogo (catalog_data.json):**
```json
{
  "content_20251020123456": {
    "title": "Strip Tease Sensual",
    "description": "Vídeo de strip tease com lingerie vermelha",
    "category": "solo",
    "content_type": "video",
    "price": 50.00,
    "preview_file_id": "telegram_file_id",
    "content_file_ids": ["telegram_file_id"],
    "duration": "5 min",
    "created_at": "2025-10-20T10:30:00",
    "active": true
  }
}
```

### **Compras (purchases_data.json):**
```json
{
  "purchase_20251020123456_7004434046": {
    "user_id": 7004434046,
    "content_id": "content_20251020123456",
    "payment_id": "pix_payment_id",
    "amount": 50.00,
    "status": "completed",
    "purchased_at": "2025-10-20T10:30:00",
    "delivered": true
  }
}
```

---

## 🔔 **NOTIFICAÇÕES**

### **Para o Admin:**
Quando um pagamento é confirmado, o admin recebe:
```
💰 PAGAMENTO CONFIRMADO - CATÁLOGO!

Usuário: [User 7004434046](link clicável)
ID: 7004434046

Conteúdo: Strip Tease Sensual
Valor: R$ 50.00

Payment ID: pix_12345

*Clique no nome do usuário para abrir conversa direta.*
```

### **Para o Usuário:**
Após pagamento:
1. Mensagem: "🎉 Pagamento Confirmado!"
2. Envio automático do(s) arquivo(s) comprado(s)
3. Mensagem: "✅ Entrega concluída!"

---

## 📋 **CATEGORIAS DISPONÍVEIS**

| Categoria | Emoji | Descrição |
|-----------|-------|-----------|
| `solo` | 💋 | Conteúdos solo exclusivos |
| `duo` | 👯 | Conteúdos com outras modelos |
| `fetiche` | 🔥 | Conteúdos de fetiche específicos |
| `personalizados` | ⭐ | Conteúdos feitos sob encomenda |
| `outros` | 📹 | Outros conteúdos exclusivos |

---

## 🔒 **SEGURANÇA**

- ✅ Apenas admins podem adicionar/remover conteúdos
- ✅ Todos os pagamentos são validados via LivePix API
- ✅ Sistema anti-fraude (ban automático para não-pagadores)
- ✅ Dashboard protegido por senha
- ✅ Logs detalhados de todas as operações

---

## 🎨 **CUSTOMIZAÇÃO**

### **Mudar Senha do Dashboard:**
Em `dashboard.py`, linha 20:
```python
ADMIN_PASSWORD = "SuaNovaSenha123!"
```

Ou via variável de ambiente:
```bash
export DASHBOARD_PASSWORD="SuaNovaSenha123!"
```

### **Adicionar Nova Categoria:**
Em `catalog_system.py`, adicione na seção `CATEGORIES`:
```python
CATEGORIES = {
    # ... categorias existentes
    "nova_categoria": {
        "name": "Nova Categoria",
        "emoji": "🎭",
        "description": "Descrição da nova categoria"
    }
}
```

---

## 📞 **SUPORTE**

Em caso de problemas:
1. Verifique os logs no terminal
2. Verifique os arquivos `.json` para inconsistências
3. Teste o sistema com valores baixos primeiro

---

## ✅ **CHECKLIST DE IMPLEMENTAÇÃO**

- [x] Sistema de catálogo com JSON
- [x] Menus de navegação para usuários
- [x] Compra com PIX integrada
- [x] Entrega automática de conteúdo
- [x] Comandos admin para gerenciar catálogo
- [x] Dashboard web com estatísticas
- [x] Notificações para admin
- [x] Sistema de preview
- [x] Organização por categorias

---

## 🚨 **IMPORTANTE**

1. **Backup Regular:** Faça backup dos arquivos `.json` regularmente
2. **Teste Primeiro:** Teste com preços baixos antes de usar em produção
3. **LivePix:** Certifique-se que sua conta LivePix está ativa e configurada
4. **Permissões do Bot:** O bot precisa poder enviar arquivos grandes

---

## 💡 **PRÓXIMOS PASSOS SUGERIDOS**

1. ✅ **Implementado:** Sistema básico funcionando
2. 🔜 **Sugerido:** Sistema de cupons de desconto
3. 🔜 **Sugerido:** Pacotes/Bundles (compre 3 pague 2)
4. 🔜 **Sugerido:** Sistema de avaliações/reviews
5. 🔜 **Sugerido:** Notificações push quando novos conteúdos são adicionados

---

**Desenvolvido para GirlfrienDine Bot** 💎

