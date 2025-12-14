"""
Integração do Sistema de Catálogo ao Bot
Este arquivo contém todas as funções necessárias para integrar o catálogo de conteúdos ao bot
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from catalog_system import (
    load_catalog, load_purchases, create_purchase,
    get_contents_by_category, get_content, CATEGORIES,
    mark_purchase_completed, mark_purchase_delivered,
    get_purchase_by_payment_id
)
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# FUNÇÕES DE ESCAPE MARKDOWN V2
# =============================================================================

def escape_markdown_v2(text: str) -> str:
    """Escapa caracteres especiais para MarkdownV2"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_price(price: float) -> str:
    """Formata preço em BRL"""
    return f"R$ {price:.2f}".replace('.', ',')

async def send_pix_payment_info(bot, chat_id: int, qr_code_base64, pix_copy_paste, 
                                 amount: float, description: str, payment_id: str) -> bool:
    """
    Envia informações de pagamento PIX (QR Code como imagem ou código copia e cola)
    """
    import base64
    import io
    
    try:
        # Tentar enviar QR Code como imagem primeiro
        if qr_code_base64:
            try:
                # Decodificar base64
                qr_image_data = base64.b64decode(qr_code_base64)
                qr_image = io.BytesIO(qr_image_data)
                qr_image.name = 'qrcode.png'
                
                # Enviar imagem do QR Code
                caption = f"""💳 **PIX Gerado com Sucesso\\!**

**Valor:** R$ {escape_markdown_v2(format_price(amount))}
**Descrição:** {escape_markdown_v2(description)}

📱 **Escaneie o QR Code acima com o app do seu banco**

⏰ **Pagamento expira em 30 minutos**
🔄 **Status:** Aguardando pagamento\\.\\.\\.

*Você receberá confirmação assim que o pagamento for processado\\!*"""
                
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=qr_image,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                
                # Se também houver código copia e cola, enviar separadamente
                if pix_copy_paste:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"""📋 **Código PIX Copia e Cola:**

`{escape_markdown_v2(pix_copy_paste)}`

*Copie o código acima e cole no app do seu banco para pagar\\!*""",
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                
                logger.info(f"QR Code sent successfully for payment {payment_id}")
                return True
                
            except Exception as e:
                logger.warning(f"Failed to send QR code as image: {e}, trying text fallback")
        
        # Fallback: enviar código copia e cola como texto
        if pix_copy_paste:
            message = f"""💳 **PIX Gerado com Sucesso\\!**

**Valor:** R$ {escape_markdown_v2(format_price(amount))}
**Descrição:** {escape_markdown_v2(description)}

📋 **Código PIX Copia e Cola:**

`{escape_markdown_v2(pix_copy_paste)}`

📱 **Instruções:**
1\\. Copie o código acima
2\\. Abra o app do seu banco
3\\. Cole o código na opção "Pagar com PIX"
4\\. Confirme o pagamento

⏰ **Pagamento expira em 30 minutos**
🔄 **Status:** Aguardando pagamento\\.\\.\\.

*Você receberá confirmação assim que o pagamento for processado\\!*"""
            
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            
            logger.info(f"PIX copy-paste code sent successfully for payment {payment_id}")
            return True
        
        # Se não houver nem QR code nem código copia e cola
        logger.error(f"No QR code or copy-paste code available for payment {payment_id}")
        await bot.send_message(
            chat_id=chat_id,
            text="❌ Erro ao gerar informações de pagamento\\. Tente novamente\\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return False
        
    except Exception as e:
        logger.error(f"Error sending PIX payment info: {e}")
        return False

# =============================================================================
# MENU DE CATÁLOGO - CATEGORIAS
# =============================================================================

async def handle_catalog_menu(query) -> None:
    """Exibe menu principal do catálogo com categorias"""
    
    message = """
📹 **CATÁLOGO DE CONTEÚDOS** 📹

*Escolha uma categoria para ver os conteúdos disponíveis:*

💋 **Solo** \\- Conteúdos solo exclusivos
👯 **Duo/Grupo** \\- Com outras modelos
🔥 **Fetiche** \\- Conteúdos de fetiche
⭐ **Personalizados** \\- Feitos sob encomenda
📹 **Outros** \\- Outros conteúdos exclusivos
"""
    
    keyboard = []
    for cat_key, cat_info in CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(
            f"{cat_info['emoji']} {cat_info['name']}",
            callback_data=f"cat_{cat_key}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )

# =============================================================================
# VISUALIZAÇÃO DE CONTEÚDOS POR CATEGORIA
# =============================================================================

async def handle_category_contents(query, category: str) -> None:
    """Exibe conteúdos de uma categoria específica"""
    
    contents = get_contents_by_category(category)
    cat_info = CATEGORIES.get(category, {})
    
    if not contents:
        message = f"""
{cat_info.get('emoji', '📹')} **{cat_info.get('name', 'Categoria').upper()}**

*Nenhum conteúdo disponível nesta categoria no momento\\.*

_Novos conteúdos são adicionados regularmente\\!_
"""
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="catalog")]]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return
    
    # Listar conteúdos
    message = f"{cat_info.get('emoji', '📹')} **{cat_info.get('name', 'Categoria').upper()}**\\n\\n"
    
    keyboard = []
    for content in contents[:10]:  # Limitar a 10 por página
        title = escape_markdown_v2(content.get('title', 'Sem título'))
        price = content.get('price', 0)
        content_type = content.get('content_type', 'video')
        
        icon = "🎥" if content_type == "video" else "📸"
        
        message += f"{icon} **{title}** \\- R$ {price:.2f}\\n"
        
        keyboard.append([InlineKeyboardButton(
            f"{icon} {content.get('title', 'Sem título')} - R$ {price:.2f}",
            callback_data=f"view_content_{content['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="catalog")])
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2
    )

# =============================================================================
# VISUALIZAÇÃO DETALHADA DE CONTEÚDO
# =============================================================================

async def handle_content_view(query, content_id: str) -> None:
    """Exibe detalhes de um conteúdo específico"""
    
    content = get_content(content_id)
    
    if not content:
        await query.answer("Conteúdo não encontrado!")
        return
    
    title = escape_markdown_v2(content.get('title', 'Sem título'))
    description = escape_markdown_v2(content.get('description', 'Sem descrição'))
    price = content.get('price', 0)
    content_type = content.get('content_type', 'video')
    
    icon = "🎥" if content_type == "video" else "📸"
    
    message = f"""
{icon} **{title}**

**Descrição:**
{description}

**Tipo:** {escape_markdown_v2(content_type.replace('_', ' ').title())}
**Preço:** R$ {price:.2f}
"""
    
    # Adicionar informações extras baseadas no tipo
    if content_type == "video":
        duration = content.get('duration', 'N/A')
        message += f"**Duração:** {escape_markdown_v2(duration)}\\n"
    elif content_type == "photo_pack":
        quantity = content.get('quantity', 0)
        message += f"**Quantidade:** {quantity} fotos\\n"
    
    message += "\n⚠️ **Aviso Importante:**\n"
    message += "*Gerar o PIX e não efetuar o pagamento resultará em bloqueio permanente do bot\\. "
    message += "Peço por gentileza que só confirme se realmente for pagar\\. Obrigada pela compreensão\\!* ❤️"
    
    keyboard = [
        [InlineKeyboardButton("💳 Comprar Agora", callback_data=f"buy_content_{content_id}")],
        [InlineKeyboardButton("👁️ Ver Preview", callback_data=f"preview_content_{content_id}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data=f"cat_{content.get('category', 'outros')}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Se houver preview, enviar
    preview_file_id = content.get('preview_file_id')
    if preview_file_id:
        try:
            await query.message.delete()
            if content_type == "video":
                await query.message.reply_animation(
                    animation=preview_file_id,
                    caption=message,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                await query.message.reply_photo(
                    photo=preview_file_id,
                    caption=message,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            return
        except Exception as e:
            logger.error(f"Error sending preview: {e}")
    
    # Se não houver preview ou erro, apenas texto
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )

# =============================================================================
# PROCESSAMENTO DE COMPRA
# =============================================================================

async def handle_content_purchase(query, content_id: str, efi_api, ADMIN_CHAT_ID: int) -> None:
    """Processa compra de conteúdo do catálogo"""
    import time
    
    user = query.from_user
    content = get_content(content_id)
    
    if not content:
        await query.answer("Conteúdo não encontrado!")
        return
    
    price = content.get('price', 0)
    title = content.get('title', 'Conteúdo')
    
    # Criar pagamento via Efi Architect API
    try:
        payment_response = efi_api.create_payment(
            valor=price,
            id_cliente=str(user.id)
        )
        
        if not payment_response:
            await query.edit_message_text(
                "❌ Erro ao gerar pagamento\\. Tente novamente mais tarde\\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
        
        # Extract payment data from orchestrator response
        qr_code_base64 = payment_response.get('qr_code_base64')
        pix_copy_paste = payment_response.get('pix_copy_paste')
        payment_id = payment_response.get('payment_id') or payment_response.get('id') or str(int(time.time()))
        
        if not qr_code_base64 and not pix_copy_paste:
            await query.edit_message_text(
                "❌ Erro ao processar resposta do pagamento\\. Tente novamente\\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            logger.error(f"Missing QR code or copy-paste code in response: {payment_response}")
            return
        
        # Criar registro de compra
        purchase_id = create_purchase(
            user_id=user.id,
            content_id=content_id,
            payment_id=payment_id,
            amount=price
        )
        
        logger.info(f"Content purchase created: {purchase_id} for user {user.id}")
        
        # Edit message to show processing
        await query.edit_message_text(
            "⏳ Gerando PIX\\.\\.\\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
        # Send PIX payment info (QR code or copy-paste)
        description = f"Catálogo: {title}"
        bot = query.bot
        success = await send_pix_payment_info(
            bot=bot,
            chat_id=user.id,
            qr_code_base64=qr_code_base64,
            pix_copy_paste=pix_copy_paste,
            amount=price,
            description=description,
            payment_id=payment_id
        )
        
        if success:
            # Send purchase ID and keyboard
            title_escaped = escape_markdown_v2(title)
            purchase_message = f"""
**ID do Pedido:** `{escape_markdown_v2(purchase_id)}`

*Após o pagamento, o conteúdo será entregue automaticamente\\.*"""
            
            keyboard = [[InlineKeyboardButton("🔙 Voltar ao Catálogo", callback_data="catalog")]]
            
            await bot.send_message(
                chat_id=user.id,
                text=purchase_message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        
    except Exception as e:
        logger.error(f"Error creating content payment: {e}")
        await query.edit_message_text(
            f"❌ Erro ao processar compra: {escape_markdown_v2(str(e))}",
            parse_mode=ParseMode.MARKDOWN_V2
        )

# =============================================================================
# ENTREGA AUTOMÁTICA DE CONTEÚDO
# =============================================================================

async def deliver_content(bot, user_id: int, content_id: str, purchase_id: str, ADMIN_CHAT_ID: int) -> bool:
    """Entrega conteúdo comprado ao usuário"""
    
    content = get_content(content_id)
    
    if not content:
        logger.error(f"Content {content_id} not found for delivery")
        return False
    
    title = content.get('title', 'Seu conteúdo')
    content_file_ids = content.get('content_file_ids', [])
    
    if not content_file_ids:
        logger.error(f"No content files for {content_id}")
        return False
    
    try:
        # Enviar mensagem inicial
        await bot.send_message(
            chat_id=user_id,
            text=f"🎉 **Pagamento Confirmado\\!**\\n\\n"
                 f"Enviando seu conteúdo: **{escape_markdown_v2(title)}**\\.\\.\\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
        # Enviar arquivos
        content_type = content.get('content_type', 'video')
        
        for file_id in content_file_ids:
            if content_type == "video":
                await bot.send_video(
                    chat_id=user_id,
                    video=file_id,
                    caption=f"📹 {escape_markdown_v2(title)}",
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            else:  # photo_pack
                await bot.send_photo(
                    chat_id=user_id,
                    photo=file_id,
                    caption=f"📸 {escape_markdown_v2(title)}",
                    parse_mode=ParseMode.MARKDOWN_V2
                )
        
        # Mensagem final
        await bot.send_message(
            chat_id=user_id,
            text="✅ **Entrega concluída\\!**\\n\\n"
                 "*Obrigada pela compra\\!* ❤️\\n\\n"
                 "Volte sempre para ver novos conteúdos\\!",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
        # Marcar como entregue
        mark_purchase_delivered(purchase_id)
        
        # Notificar admin
        user_link = f"[{escape_markdown_v2(f'User {user_id}')}](tg://user?id={user_id})"
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"✅ **Conteúdo Entregue\\!**\\n\\n"
                 f"**Usuário:** {user_link}\\n"
                 f"**Conteúdo:** {escape_markdown_v2(title)}\\n"
                 f"**Pedido:** `{escape_markdown_v2(purchase_id)}`",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
        logger.info(f"Content delivered successfully: {content_id} to user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error delivering content: {e}")
        return False

# =============================================================================
# NOTIFICAÇÃO DE PAGAMENTO PARA ADMIN
# =============================================================================

async def notify_admin_content_payment(bot, user_id: int, content_id: str, amount: float, payment_id: str, ADMIN_CHAT_ID: int) -> None:
    """Notifica admin sobre pagamento de conteúdo confirmado"""
    
    content = get_content(content_id)
    title = content.get('title', 'N/A') if content else 'N/A'
    
    user_link = f"[User {user_id}](tg://user?id={user_id})"
    
    message = f"""
💰 **PAGAMENTO CONFIRMADO \\- CATÁLOGO\\!**

**Usuário:** {user_link}
**ID:** `{user_id}`

**Conteúdo:** {escape_markdown_v2(title)}
**Valor:** R$ {amount:.2f}

**Payment ID:** `{escape_markdown_v2(payment_id)}`

*Clique no nome do usuário para abrir conversa direta\\.*
"""
    
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        logger.info(f"Admin notified of content payment from user {user_id}")
    except Exception as e:
        logger.error(f"Error notifying admin: {e}")

