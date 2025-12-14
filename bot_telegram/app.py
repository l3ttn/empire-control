#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Microserviço de Orquestração PIX (Efí Bank) - FastAPI Async
Webhook handler para notificações de pagamento PIX com Fallback e Upsell
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import httpx
from fastapi import FastAPI, Request, HTTPException, Header, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, DateTime, Integer, Text

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações (REQUIRED - NO FALLBACKS FOR SECURITY)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("CRÍTICO: TELEGRAM_BOT_TOKEN não encontrado! Configure no arquivo .env")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

EFI_WEBHOOK_SECRET = os.getenv("EFI_WEBHOOK_SECRET")
if not EFI_WEBHOOK_SECRET:
    raise ValueError("CRÍTICO: EFI_WEBHOOK_SECRET não encontrado! Configure no arquivo .env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./pix_orchestrator.db")

# Inicializar FastAPI
app = FastAPI(
    title="PIX Orchestrator API",
    description="Microserviço de Orquestração PIX (Efí Bank) com Fallback e Upsell",
    version="2.0.0"
)

# SQLAlchemy Async Setup
Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Modelos de Banco de Dados
class PaymentRecord(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String, unique=True, index=True)
    client_id = Column(String, index=True)
    valor = Column(Float)
    status = Column(String)
    qr_code_base64 = Column(Text, nullable=True)
    pix_copy_paste = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Criar tabelas
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

# Modelos Pydantic
class ProcessarPixRequest(BaseModel):
    valor: float = Field(..., gt=0, description="Valor do pagamento em reais")
    id_cliente: str = Field(..., description="ID do cliente Telegram")

class ProcessarPixResponse(BaseModel):
    payment_id: str
    qr_code_base64: Optional[str] = None
    pix_copy_paste: Optional[str] = None
    status: str

class WebhookPixRequest(BaseModel):
    status: str
    client_id: Optional[str] = None
    valor: Optional[float] = None
    payment_id: Optional[str] = None

# Funções auxiliares
async def verify_webhook_token(x_callback_token: Optional[str] = None) -> bool:
    """
    Verifica o token de segurança do webhook do Efí Bank
    
    Args:
        x_callback_token: Token recebido no header X-Callback-Token
        
    Returns:
        True se o token for válido, False caso contrário
    """
    if not EFI_WEBHOOK_SECRET:
        logger.error("EFI_WEBHOOK_SECRET not configured in environment variables!")
        return False
    
    if not x_callback_token:
        logger.warning("Webhook request missing X-Callback-Token header")
        return False
    
    # Comparar com o secret configurado
    if x_callback_token != EFI_WEBHOOK_SECRET:
        logger.warning(f"Invalid webhook token received. Expected: {EFI_WEBHOOK_SECRET[:10]}..., Got: {x_callback_token[:10]}...")
        return False
    
    return True

async def send_telegram_message(chat_id: str, message: str) -> bool:
    """
    Envia mensagem para o Telegram usando a API oficial (assíncrono)
    
    Args:
        chat_id: ID do usuário Telegram (client_id)
        message: Mensagem a ser enviada
        
    Returns:
        True se enviado com sucesso, False caso contrário
    """
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "MarkdownV2"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to Telegram user {chat_id}")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False

async def send_upsell_message(client_id: str, valor_pago: float) -> None:
    """
    Envia mensagem de upsell após confirmação de pagamento
    
    Args:
        client_id: ID do cliente Telegram
        valor_pago: Valor que foi pago
    """
    try:
        # Lógica de upsell baseada no valor pago
        if valor_pago < 100:
            upsell_message = """🎁 **Oferta Especial para Você!**

Aproveite nosso plano VIP com desconto exclusivo!

💎 **Benefícios:**
• Acesso total ao grupo VIP
• Conteúdo exclusivo diário
• Descontos em todos os serviços

*Entre em contato para saber mais!*"""
        elif valor_pago < 300:
            upsell_message = """🔥 **Upgrade para Plano Anual!**

Economize ainda mais com nosso plano anual!

💰 **Economia de até R$ 180!**
• 12 meses de acesso
• Melhor custo-benefício
• Renovação automática

*Pergunte sobre nossos planos!*"""
        else:
            # Cliente já pagou valor alto, não enviar upsell
            return
        
        await send_telegram_message(client_id, upsell_message)
        logger.info(f"Upsell message sent to client {client_id}")
        
    except Exception as e:
        logger.error(f"Error sending upsell message: {e}")

# Endpoints
@app.post("/processar_pix", response_model=ProcessarPixResponse)
async def processar_pix(request: ProcessarPixRequest):
    """
    Processa uma solicitação de pagamento PIX
    
    Este endpoint recebe a requisição do bot e cria o pagamento PIX
    através da integração com Efí Bank (com fallback)
    """
    try:
        # Tentar criar pagamento via Efí Bank (método principal)
        try:
            # Aqui você integraria com a API real do Efí Bank
            # Por enquanto, simulamos uma resposta de sucesso
            payment_id = f"pix_{int(datetime.utcnow().timestamp())}_{request.id_cliente}"
            
            # Simular resposta da API Efí Bank
            qr_code_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="  # QR code placeholder
            pix_copy_paste = f"00020126580014BR.GOV.BCB.PIX0136{payment_id}5204000053039865802BR5913TESTE MERCADO6008BRASILIA62070503***6304ABCD"
            
            # Salvar no banco de dados
            async with AsyncSessionLocal() as session:
                payment_record = PaymentRecord(
                    payment_id=payment_id,
                    client_id=request.id_cliente,
                    valor=request.valor,
                    status="PENDENTE",
                    qr_code_base64=qr_code_base64,
                    pix_copy_paste=pix_copy_paste
                )
                session.add(payment_record)
                await session.commit()
            
            logger.info(f"Payment created successfully: {payment_id} for client {request.id_cliente}")
            
            return ProcessarPixResponse(
                payment_id=payment_id,
                qr_code_base64=qr_code_base64,
                pix_copy_paste=pix_copy_paste,
                status="PENDENTE"
            )
            
        except Exception as e:
            logger.error(f"Error creating payment via Efí Bank (primary method): {e}")
            
            # FALLBACK: Tentar método alternativo
            try:
                logger.info("Attempting fallback payment method...")
                
                # Aqui você implementaria um método alternativo de pagamento
                # Por exemplo, gerar QR code manualmente ou usar outro provedor
                payment_id = f"pix_fallback_{int(datetime.utcnow().timestamp())}_{request.id_cliente}"
                
                # Gerar QR code básico como fallback
                pix_copy_paste = f"00020126580014BR.GOV.BCB.PIX0136{payment_id}5204000053039865802BR5913FALLBACK6008BRASILIA62070503***6304FALL"
                
                # Salvar no banco de dados
                async with AsyncSessionLocal() as session:
                    payment_record = PaymentRecord(
                        payment_id=payment_id,
                        client_id=request.id_cliente,
                        valor=request.valor,
                        status="PENDENTE_FALLBACK",
                        pix_copy_paste=pix_copy_paste
                    )
                    session.add(payment_record)
                    await session.commit()
                
                logger.warning(f"Payment created via fallback method: {payment_id}")
                
                return ProcessarPixResponse(
                    payment_id=payment_id,
                    qr_code_base64=None,
                    pix_copy_paste=pix_copy_paste,
                    status="PENDENTE_FALLBACK"
                )
                
            except Exception as fallback_error:
                logger.error(f"Fallback payment method also failed: {fallback_error}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Payment service temporarily unavailable. Please try again later."
                )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing PIX payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing payment"
        )

@app.post("/webhook/pix")
async def webhook_pix(
    request: WebhookPixRequest,
    x_callback_token: Optional[str] = Header(None, alias="X-Callback-Token")
):
    """
    Webhook para receber notificações de pagamento PIX do orquestrador
    
    Segurança: Requer header X-Callback-Token válido
    """
    # VERIFICAÇÃO DE SEGURANÇA CRÍTICA - ANTES DE PROCESSAR QUALQUER DADO
    if not await verify_webhook_token(x_callback_token):
        logger.warning("Unauthorized webhook attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    
    try:
        status_payment = request.status.upper()
        client_id = request.client_id
        
        logger.info(f"Webhook received: status={status_payment}, client_id={client_id}")
        
        # Verificar se o pagamento foi concluído
        if status_payment == 'CONCLUIDA':
            if not client_id:
                logger.error("Webhook missing client_id for CONCLUIDA status")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing client_id"
                )
            
            # Atualizar status no banco de dados
            if request.payment_id:
                async with AsyncSessionLocal() as session:
                    from sqlalchemy import select, update
                    # Buscar pagamento
                    stmt = select(PaymentRecord).where(PaymentRecord.payment_id == request.payment_id)
                    result = await session.execute(stmt)
                    payment = result.scalar_one_or_none()
                    
                    if payment:
                        # Atualizar status
                        payment.status = 'CONCLUIDA'
                        payment.updated_at = datetime.utcnow()
                        await session.commit()
                        logger.info(f"Payment {request.payment_id} status updated to CONCLUIDA")
            
            # Enviar mensagem de confirmação para o Telegram
            message = "✅ Pagamento confirmado! Seu acesso foi liberado."
            
            success = await send_telegram_message(
                chat_id=str(client_id),
                message=message
            )
            
            if success:
                logger.info(f"Payment confirmation sent to Telegram user {client_id}")
                
                # Registrar venda no Google Sheets (Empire Control sync)
                valor_pago = request.valor or 0.0
                try:
                    from gsheets_integration import registrar_venda_bot
                    registrar_venda_bot(
                        client_id=str(client_id),
                        conteudo="Pagamento PIX",
                        valor=valor_pago,
                        payment_id=request.payment_id or "unknown"
                    )
                    logger.info(f"Sale registered in Google Sheets for client {client_id}")
                except Exception as gsheets_error:
                    # Nao bloquear se Google Sheets falhar
                    logger.warning(f"Failed to register sale in Google Sheets: {gsheets_error}")
                
                # Enviar mensagem de upsell após confirmação
                await send_upsell_message(str(client_id), valor_pago)
                
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"status": "success", "message": "Notification sent"}
                )
            else:
                logger.error(f"Failed to send payment confirmation to Telegram user {client_id}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"status": "error", "message": "Failed to send notification"}
                )
        else:
            # Status não é CONCLUIDA, apenas logar
            logger.info(f"Webhook received with status {status_payment}, no action needed")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "received", "message": "Webhook processed"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PIX Orchestrator API"}

@app.get("/")
async def index():
    """Root endpoint"""
    return {
        "service": "PIX Orchestrator Webhook Handler",
        "version": "2.0.0",
        "stack": "FastAPI + SQLAlchemy Async",
        "endpoints": {
            "processar_pix": "/processar_pix",
            "webhook": "/webhook/pix",
            "health": "/health"
        }
    }
