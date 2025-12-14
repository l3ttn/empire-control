# 🔒 RECURSOS DE SEGURANÇA DO BOT

## ✅ Proteções Implementadas

### 1️⃣ **Proteção de Comandos Admin**
- **Decorador `@admin_only`**: Todos os comandos administrativos agora possuem verificação rigorosa
- **Lista de IDs autorizados**: Apenas IDs em `ALLOWED_ADMIN_IDS` podem executar comandos privilegiados
- **Sem resposta para não-admins**: Usuários não autorizados não recebem nenhuma resposta ao tentar comandos admin, evitando engenharia social
- **Logging de tentativas**: Todas as tentativas de acesso não autorizado são registradas com detalhes do usuário

**Comandos Protegidos:**
- `/addvip` - Adicionar VIP manualmente
- `/removevip` - Remover VIP
- `/listvip` - Listar VIPs ativos
- `/checkvip` - Checar status VIP
- `/setvipdays` - Definir dias VIP (teste)
- `/ban` - Banir usuário
- `/unban` - Desbanir usuário
- `/listbans` - Listar banidos
- `/online` - Anunciar online
- `/offline` - Anunciar offline
- `/promo` - Enviar promoção
- `/post` - Post personalizado
- `/admin` - Menu admin

### 2️⃣ **Proteção do Grupo VIP - Anti-Bot**
- **Detecção automática de bots**: Qualquer bot adicionado ao grupo VIP (exceto o bot oficial) é banido imediatamente
- **Notificação ao admin**: Admin recebe alerta quando um bot é detectado e removido
- **Logging completo**: Todas as ações são registradas para auditoria

### 3️⃣ **Proteção Anti-Download**
- **Monitoramento de comandos suspeitos**: O bot monitora mensagens no grupo VIP em busca de comandos de download
- **Comandos bloqueados**:
  - `/save` - Salvar arquivos
  - `/download` - Baixar conteúdo
  - `/get` - Obter arquivos
  - `/dl` - Download
  - `/fetch` - Buscar arquivos
  - `@bot` - Menções a bots de terceiros
  
- **Ações automáticas**:
  1. Mensagem suspeita é deletada imediatamente
  2. Usuário recebe aviso privado sobre as regras
  3. Admin é notificado da atividade suspeita
  4. Tentativas repetidas podem resultar em banimento

### 4️⃣ **Proteção Contra Engenharia Social**
- **Nenhuma resposta a não-admins**: Comandos admin não retornam nenhuma mensagem para usuários não autorizados
- **Logs de segurança**: Todas as tentativas são registradas com:
  - User ID
  - Username
  - Comando tentado
  - Timestamp

## 🛡️ Boas Práticas Adicionais

### Para Máxima Segurança:

1. **Configure o grupo VIP corretamente**:
   - Desabilite "Adicionar novos membros" para todos (apenas admins)
   - Desabilite "Enviar mensagens" temporariamente se necessário
   - Habilite "Aprovar novos membros" se disponível

2. **Configurações recomendadas do Telegram**:
   - Ative proteção contra spam
   - Desabilite links de convite permanentes
   - Use links de convite temporários (gerados pelo bot após pagamento)

3. **Monitoramento**:
   - Revise os logs regularmente
   - Monitore alertas de segurança
   - Verifique tentativas de acesso não autorizado

4. **Limitação Física**:
   ⚠️ **IMPORTANTE**: O Telegram NÃO permite impedir 100% o download de arquivos por usuários. Mesmo com todas as proteções:
   - Usuários podem fazer screenshot
   - Usuários podem usar apps de terceiros
   - Usuários podem gravar tela
   
   **Solução**: 
   - Marque todo conteúdo com watermark (nome do usuário)
   - Use conteúdo temporário (que se autodestrue)
   - Considere usar "View Once" para fotos/vídeos

## 📊 Logs de Segurança

Todos os eventos de segurança são registrados em `bot.log`:

```
SECURITY ALERT: Unauthorized admin command attempt by user 123456 (@hacker) - Command: /addvip
SECURITY: Bot detected in VIP group: @SaveContentBot (ID: 987654). Removing immediately.
SECURITY: Suspicious command detected from user 456789 (@user): /download
```

## 🚨 Em Caso de Violação

Se detectar atividade suspeita:

1. Use `/ban <user_id>` para banir o usuário
2. Revise os logs
3. Verifique se outros usuários foram afetados
4. Considere resetar os links de convite do grupo

## ⚙️ Configuração

Arquivo `.env`:
```env
TELEGRAM_ADMIN_ID=7004434046  # Seu ID do Telegram
VIP_GROUP_ID=-4831001669      # ID do grupo VIP
```

**NUNCA compartilhe o arquivo `.env` ou exponha os IDs publicamente!**

