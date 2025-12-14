"""
Comandos Administrativos para Gerenciamento do Catálogo
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from catalog_system import (
    add_content, update_content, delete_content,
    get_content, get_all_active_contents, CATEGORIES
)
import logging

logger = logging.getLogger(__name__)

# Estados para adicionar conteúdo
user_content_states = {}

def escape_markdown_v2(text: str) -> str:
    """Escapa caracteres especiais para MarkdownV2"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

# =============================================================================
# COMANDO: /addcontent - Adicionar Conteúdo ao Catálogo
# =============================================================================

async def admin_addcontent_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Admin command to add content to catalog
    Usage: 
    1. Send /addcontent
    2. Bot asks for video/photo
    3. Send media
    4. Bot asks for details
    5. Provide details in format:
       Título
       Descrição
       Categoria (solo/duo/fetiche/personalizados/outros)
       Preço
       Duração (para vídeos) ou Quantidade (para packs)
    """
    user_id = update.effective_user.id
    
    help_text = """
📹 **Adicionar Conteúdo ao Catálogo**

**Passo 1:** Envie o vídeo ou foto\\(s\\) do conteúdo completo

**Passo 2:** Envie uma preview \\(GIF ou foto\\)

**Passo 3:** Envie os detalhes no formato:

```
Título do Conteúdo
Descrição detalhada
Categoria \\(solo/duo/fetiche/personalizados/outros\\)
Preço \\(apenas número\\)
Duração \\(ex: 5 min\\) ou Quantidade \\(ex: 10\\)
```

**Exemplo:**
```
Strip Tease Sensual
Vídeo de strip tease com lingerie vermelha
solo
50
5 min
```

*Envie o conteúdo para começar\\!*
"""
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN_V2)
    
    # Iniciar estado
    user_content_states[user_id] = {
        'step': 'awaiting_content_files',
        'content_file_ids': [],
        'preview_file_id': None
    }

# =============================================================================
# COMANDO: /listcatalog - Listar Conteúdos do Catálogo
# =============================================================================

async def admin_listcatalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to list all catalog contents"""
    
    contents = get_all_active_contents()
    
    if not contents:
        await update.message.reply_text(
            "📭 Catálogo vazio\\. Use /addcontent para adicionar\\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return
    
    message = "📹 **CATÁLOGO \\- TODOS OS CONTEÚDOS**\\n\\n"
    
    # Agrupar por categoria
    by_category = {}
    for content in contents:
        cat = content.get('category', 'outros')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(content)
    
    for cat_key, cat_contents in by_category.items():
        cat_info = CATEGORIES.get(cat_key, {'name': cat_key.title(), 'emoji': '📹'})
        message += f"\\n{cat_info['emoji']} **{cat_info['name'].upper()}**\\n"
        
        for content in cat_contents:
            title = escape_markdown_v2(content.get('title', 'Sem título'))
            price = content.get('price', 0)
            content_id = escape_markdown_v2(content['id'])
            
            message += f"• {title} \\- R$ {price:.2f}\\n"
            message += f"  ID: `{content_id}`\\n"
    
    message += f"\\n**Total:** {len(contents)} conteúdo\\(s\\)"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

# =============================================================================
# COMANDO: /removecontent - Remover Conteúdo
# =============================================================================

async def admin_removecontent_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Admin command to remove content from catalog
    Usage: /removecontent <content_id>
    """
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Uso incorreto\\!\n\n"
            "**Formato:** `/removecontent <content_id>`\n\n"
            "**Exemplo:** `/removecontent content_20251020123456`",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return
    
    content_id = context.args[0]
    
    # Verificar se existe
    content = get_content(content_id)
    if not content:
        await update.message.reply_text(
            f"❌ Conteúdo `{escape_markdown_v2(content_id)}` não encontrado\\!",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return
    
    # Remover (soft delete)
    if delete_content(content_id):
        title = escape_markdown_v2(content.get('title', 'N/A'))
        await update.message.reply_text(
            f"✅ Conteúdo removido com sucesso\\!\n\n"
            f"**Título:** {title}\n"
            f"**ID:** `{escape_markdown_v2(content_id)}`",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        logger.info(f"Content {content_id} removed from catalog")
    else:
        await update.message.reply_text(
            "❌ Erro ao remover conteúdo\\!",
            parse_mode=ParseMode.MARKDOWN_V2
        )

# =============================================================================
# COMANDO: /catalogstats - Estatísticas do Catálogo
# =============================================================================

async def admin_catalogstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to show catalog statistics"""
    from catalog_system import load_purchases
    
    contents = get_all_active_contents()
    purchases = load_purchases()
    
    total_contents = len(contents)
    total_sales = len([p for p in purchases.values() if p.get('status') == 'completed'])
    total_revenue = sum([p.get('amount', 0) for p in purchases.values() if p.get('status') == 'completed'])
    
    # Contar por categoria
    by_category = {}
    for content in contents:
        cat = content.get('category', 'outros')
        by_category[cat] = by_category.get(cat, 0) + 1
    
    message = "📊 **ESTATÍSTICAS DO CATÁLOGO**\\n\\n"
    message += f"**Total de Conteúdos:** {total_contents}\\n"
    message += f"**Total de Vendas:** {total_sales}\\n"
    message += f"**Receita Total:** R$ {total_revenue:.2f}\\n\\n"
    
    message += "**Por Categoria:**\\n"
    for cat_key, count in by_category.items():
        cat_info = CATEGORIES.get(cat_key, {'name': cat_key.title(), 'emoji': '📹'})
        message += f"{cat_info['emoji']} {escape_markdown_v2(cat_info['name'])}: {count}\\n"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

# =============================================================================
# HANDLER PARA PROCESSAR ADIÇÃO DE CONTEÚDO
# =============================================================================

async def process_content_addition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Processa mensagens durante adição de conteúdo
    Returns True se processou, False caso contrário
    """
    user_id = update.effective_user.id
    
    if user_id not in user_content_states:
        return False
    
    state = user_content_states[user_id]
    step = state.get('step')
    
    # Passo 1: Receber arquivos de conteúdo
    if step == 'awaiting_content_files':
        if update.message.video:
            file_id = update.message.video.file_id
            state['content_file_ids'].append(file_id)
            state['content_type'] = 'video'
            
            await update.message.reply_text(
                "✅ Vídeo recebido\\!\n\n"
                "Agora envie uma **preview** \\(GIF ou foto de capa\\)\\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            state['step'] = 'awaiting_preview'
            return True
            
        elif update.message.photo:
            file_id = update.message.photo[-1].file_id
            state['content_file_ids'].append(file_id)
            state['content_type'] = 'photo_pack'
            
            await update.message.reply_text(
                "✅ Foto recebida\\!\n\n"
                "Envie mais fotos ou envie uma **preview** para continuar\\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return True
    
    # Passo 2: Receber preview
    elif step == 'awaiting_preview':
        if update.message.animation or update.message.photo:
            file_id = update.message.animation.file_id if update.message.animation else update.message.photo[-1].file_id
            state['preview_file_id'] = file_id
            
            await update.message.reply_text(
                "✅ Preview recebida\\!\n\n"
                "Agora envie os **detalhes** no formato especificado\\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            state['step'] = 'awaiting_details'
            return True
    
    # Passo 3: Receber detalhes
    elif step == 'awaiting_details':
        if update.message.text:
            try:
                lines = update.message.text.strip().split('\n')
                
                if len(lines) < 5:
                    await update.message.reply_text(
                        "❌ Formato incorreto\\! Envie todas as 5 linhas\\.",
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                    return True
                
                title = lines[0].strip()
                description = lines[1].strip()
                category = lines[2].strip().lower()
                price = float(lines[3].strip())
                extra = lines[4].strip()
                
                # Validar categoria
                if category not in CATEGORIES:
                    await update.message.reply_text(
                        f"❌ Categoria inválida\\! Use: {escape_markdown_v2(', '.join(CATEGORIES.keys()))}",
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                    return True
                
                # Criar conteúdo
                content_data = {
                    'title': title,
                    'description': description,
                    'category': category,
                    'price': price,
                    'content_type': state['content_type'],
                    'preview_file_id': state['preview_file_id'],
                    'content_file_ids': state['content_file_ids']
                }
                
                if state['content_type'] == 'video':
                    content_data['duration'] = extra
                else:
                    content_data['quantity'] = len(state['content_file_ids'])
                
                content_id = add_content(content_data)
                
                await update.message.reply_text(
                    f"✅ **Conteúdo adicionado com sucesso\\!**\\n\\n"
                    f"**Título:** {escape_markdown_v2(title)}\\n"
                    f"**ID:** `{escape_markdown_v2(content_id)}`\\n"
                    f"**Preço:** R$ {price:.2f}",
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                
                # Limpar estado
                del user_content_states[user_id]
                logger.info(f"Content added to catalog: {content_id}")
                
                return True
                
            except Exception as e:
                logger.error(f"Error adding content: {e}")
                await update.message.reply_text(
                    f"❌ Erro ao adicionar conteúdo: {escape_markdown_v2(str(e))}",
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                return True
    
    return False

