#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Microserviço de Orquestração PIX - Multi-Provider (Mercado Pago + PagBank)
Webhook handler para notificações de pagamento PIX com Fallback automático
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

# Importar gerenciador de pagamentos (multi-provider)
from payment_manager import (
    criar_pagamento_com_fallback,
    consultar_pagamento,
    processar_webhook,
    verificar_status_provedores,
    PaymentProvider
)
from pagbank_integration import processar_webhook_pagbank

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.warning("TELEGRAM_BOT_TOKEN não encontrado! Configure no arquivo .env")
    TELEGRAM_BOT_TOKEN = "placeholder"

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Mercado Pago Webhook Secret (opcional, para verificação extra)
MP_WEBHOOK_SECRET = os.getenv("MP_WEBHOOK_SECRET", "")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./pix_orchestrator.db")

# Inicializar FastAPI
app = FastAPI(
    title="PIX Orchestrator API - Multi-Provider",
    description="Microserviço de Orquestração PIX (Mercado Pago + PagBank) com Fallback automático",
    version="4.0.0"
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
    descricao: Optional[str] = Field(default="Pagamento via Bot", description="Descrição do pagamento")

class ProcessarPixResponse(BaseModel):
    payment_id: str
    qr_code_base64: Optional[str] = None
    pix_copy_paste: Optional[str] = None
    ticket_url: Optional[str] = None
    status: str


async def send_telegram_message(chat_id: str, message: str, parse_mode: str = "Markdown") -> bool:
    """
    Envia mensagem para o Telegram usando a API oficial (assíncrono)
    """
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode
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
    """
    try:
        if valor_pago < 100:
            upsell_message = """🎁 *Oferta Especial para Você!*

Aproveite nosso plano VIP com desconto exclusivo!

💎 *Benefícios:*
• Acesso total ao grupo VIP
• Conteúdo exclusivo diário
• Descontos em todos os serviços

_Entre em contato para saber mais!_"""
        elif valor_pago < 300:
            upsell_message = """🔥 *Upgrade para Plano Anual!*

Economize ainda mais com nosso plano anual!

💰 *Economia de até R$ 180!*
• 12 meses de acesso
• Melhor custo-benefício
• Renovação automática

_Pergunte sobre nossos planos!_"""
        else:
            return
        
        await send_telegram_message(client_id, upsell_message)
        logger.info(f"Upsell message sent to client {client_id}")
        
    except Exception as e:
        logger.error(f"Error sending upsell message: {e}")


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/processar_pix", response_model=ProcessarPixResponse)
async def processar_pix(request: ProcessarPixRequest):
    """
    Processa uma solicitação de pagamento PIX (Multi-Provider com Fallback)
    Tenta o provedor principal, se falhar usa o secundário automaticamente.
    """
    try:
        # Criar referência externa para rastrear
        external_ref = f"bot_{request.id_cliente}_{int(datetime.utcnow().timestamp())}"
        
        # Criar pagamento com fallback automático
        resultado = criar_pagamento_com_fallback(
            valor=request.valor,
            descricao=request.descricao or "Pagamento via Bot",
            external_reference=external_ref,
            expiracao_minutos=30
        )
        
        if resultado.get("success"):
            payment_id = str(resultado.get("payment_id"))
            qr_code = resultado.get("qr_code")
            qr_code_base64 = resultado.get("qr_code_base64")
            ticket_url = resultado.get("ticket_url")
            
            # Salvar no banco de dados
            async with AsyncSessionLocal() as session:
                payment_record = PaymentRecord(
                    payment_id=payment_id,
                    client_id=request.id_cliente,
                    valor=request.valor,
                    status="pending",
                    qr_code_base64=qr_code_base64,
                    pix_copy_paste=qr_code
                )
                session.add(payment_record)
                await session.commit()
            
            logger.info(f"Payment created successfully: {payment_id} for client {request.id_cliente}")
            
            return ProcessarPixResponse(
                payment_id=payment_id,
                qr_code_base64=qr_code_base64,
                pix_copy_paste=qr_code,
                ticket_url=ticket_url,
                status="pending"
            )
        else:
            error_msg = resultado.get("error", "Erro desconhecido")
            logger.error(f"Failed to create payment: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Erro ao criar pagamento: {error_msg}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing PIX payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing payment"
        )


@app.post("/webhook/mercadopago")
async def webhook_mercadopago(request: Request):
    """
    Webhook para receber notificações de pagamento do Mercado Pago
    
    O Mercado Pago envia notificações quando o status do pagamento muda
    """
    try:
        # Ler body do request
        body = await request.json()
        
        logger.info(f"Webhook MP received: {body}")
        
        # Verificar se é uma notificação de pagamento
        topic = body.get("type") or body.get("topic")
        
        if topic == "payment":
            # Processar webhook
            resultado = processar_webhook_mercadopago(body)
            
            if resultado.get("success") and resultado.get("is_approved"):
                payment_id = str(resultado.get("payment_id"))
                external_ref = resultado.get("external_reference", "")
                valor = resultado.get("amount", 0)
                
                # Extrair client_id da external_reference (formato: bot_CLIENTID_TIMESTAMP)
                client_id = None
                if external_ref and external_ref.startswith("bot_"):
                    parts = external_ref.split("_")
                    if len(parts) >= 2:
                        client_id = parts[1]
                
                if client_id:
                    # Atualizar status no banco de dados
                    async with AsyncSessionLocal() as session:
                        from sqlalchemy import select
                        stmt = select(PaymentRecord).where(PaymentRecord.payment_id == payment_id)
                        result = await session.execute(stmt)
                        payment = result.scalar_one_or_none()
                        
                        if payment:
                            payment.status = 'approved'
                            payment.updated_at = datetime.utcnow()
                            await session.commit()
                            logger.info(f"Payment {payment_id} status updated to approved")
                    
                    # Enviar mensagem de confirmação
                    message = "✅ *Pagamento confirmado!*\n\nSeu acesso foi liberado. Obrigado pela compra!"
                    await send_telegram_message(chat_id=client_id, message=message)
                    
                    # Registrar venda no Google Sheets
                    try:
                        from gsheets_integration import registrar_venda_bot
                        registrar_venda_bot(
                            client_id=client_id,
                            conteudo="Pagamento PIX MP",
                            valor=valor,
                            payment_id=payment_id
                        )
                        logger.info(f"Sale registered in Google Sheets")
                    except Exception as gsheets_error:
                        logger.warning(f"Failed to register sale in GSheets: {gsheets_error}")
                    
                    # Upsell
                    await send_upsell_message(client_id, valor)
                    
                    return JSONResponse(
                        status_code=200,
                        content={"status": "success", "message": "Payment processed"}
                    )
                else:
                    logger.warning(f"Could not extract client_id from external_ref: {external_ref}")
            
            return JSONResponse(
                status_code=200,
                content={"status": "received"}
            )
        
        # Outros tipos de notificação
        return JSONResponse(status_code=200, content={"status": "ignored"})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        # Retornar 200 mesmo com erro para evitar reenvios do MP
        return JSONResponse(status_code=200, content={"status": "error", "message": str(e)})


@app.get("/payment/{payment_id}")
async def get_payment_status(payment_id: str):
    """
    Consulta status de um pagamento
    """
    resultado = consultar_pagamento(payment_id)
    
    if resultado.get("success"):
        return resultado
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=resultado.get("error", "Payment not found")
        )


@app.post("/webhook/pagbank")
async def webhook_pagbank(request: Request):
    """
    Webhook para receber notificações de pagamento do PagBank (PagSeguro)
    """
    try:
        body = await request.json()
        
        logger.info(f"Webhook PagBank received: {body}")
        
        # Processar webhook
        resultado = processar_webhook_pagbank(body)
        
        if resultado.get("success") and resultado.get("is_approved"):
            order_id = str(resultado.get("order_id"))
            reference_id = resultado.get("reference_id", "")
            valor = resultado.get("amount", 0)
            
            # Extrair client_id da reference_id (formato: bot_CLIENTID_TIMESTAMP)
            client_id = None
            if reference_id and reference_id.startswith("bot_"):
                parts = reference_id.split("_")
                if len(parts) >= 2:
                    client_id = parts[1]
            
            if client_id:
                # Atualizar status no banco de dados
                async with AsyncSessionLocal() as session:
                    from sqlalchemy import select
                    stmt = select(PaymentRecord).where(PaymentRecord.payment_id == order_id)
                    result = await session.execute(stmt)
                    payment = result.scalar_one_or_none()
                    
                    if payment:
                        payment.status = 'approved'
                        payment.updated_at = datetime.utcnow()
                        await session.commit()
                        logger.info(f"Payment {order_id} status updated to approved (PagBank)")
                
                # Enviar mensagem de confirmação
                message = "✅ *Pagamento confirmado!*\n\nSeu acesso foi liberado. Obrigado pela compra!"
                await send_telegram_message(chat_id=client_id, message=message)
                
                # Registrar venda no Google Sheets
                try:
                    from gsheets_integration import registrar_venda_bot
                    registrar_venda_bot(
                        client_id=client_id,
                        conteudo="Pagamento PIX PagBank",
                        valor=valor,
                        payment_id=order_id
                    )
                    logger.info(f"Sale registered in Google Sheets (PagBank)")
                except Exception as gsheets_error:
                    logger.warning(f"Failed to register sale in GSheets: {gsheets_error}")
                
                # Upsell
                await send_upsell_message(client_id, valor)
                
                return JSONResponse(
                    status_code=200,
                    content={"status": "success", "message": "Payment processed"}
                )
        
        return JSONResponse(status_code=200, content={"status": "received"})
        
    except Exception as e:
        logger.error(f"Error processing PagBank webhook: {e}")
        return JSONResponse(status_code=200, content={"status": "error", "message": str(e)})


@app.get("/providers/status")
async def providers_status():
    """
    Verifica status de configuração dos provedores de pagamento
    """
    return verificar_status_provedores()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PIX Orchestrator API - Multi-Provider"}

@app.get("/")
async def index():
    """Root endpoint"""
    return {
        "service": "PIX Orchestrator - Multi-Provider",
        "version": "4.0.0",
        "stack": "FastAPI + SQLAlchemy Async + Mercado Pago + PagBank",
        "active_provider": os.getenv("PAYMENT_PROVIDER", "mercadopago"),
        "endpoints": {
            "processar_pix": "/processar_pix",
            "webhook_mercadopago": "/webhook/mercadopago",
            "webhook_pagbank": "/webhook/pagbank",
            "payment_status": "/payment/{payment_id}",
            "providers_status": "/providers/status",
            "health": "/health"
        }
    }

