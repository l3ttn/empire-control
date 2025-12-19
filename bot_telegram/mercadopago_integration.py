"""
Módulo de integração com Mercado Pago para pagamentos PIX.
Gera QR Code PIX e recebe notificações via webhook.
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Access Token do Mercado Pago (obtido em https://www.mercadopago.com.br/developers/panel/app)
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "")

# URLs da API
MP_API_BASE = "https://api.mercadopago.com"

# Headers padrão
def get_headers():
    return {
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": f"{datetime.now().timestamp()}"
    }


# ============================================================================
# CRIAR PAGAMENTO PIX
# ============================================================================

def criar_pagamento_pix(
    valor: float,
    descricao: str,
    email_pagador: str = "cliente@email.com",
    external_reference: Optional[str] = None,
    expiracao_minutos: int = 30
) -> Dict[str, Any]:
    """
    Cria um pagamento PIX no Mercado Pago.
    
    Args:
        valor: Valor em reais (ex: 60.00)
        descricao: Descrição do produto/serviço
        email_pagador: Email do cliente (pode ser genérico)
        external_reference: ID externo para rastrear (ex: user_id + timestamp)
        expiracao_minutos: Tempo até o PIX expirar
    
    Returns:
        Dict com:
            - success: bool
            - payment_id: ID do pagamento
            - qr_code: String do código PIX copia-cola
            - qr_code_base64: Imagem do QR code em base64
            - ticket_url: URL para página de pagamento
            - error: mensagem de erro (se houver)
    """
    
    if not MERCADO_PAGO_ACCESS_TOKEN:
        return {"success": False, "error": "MERCADO_PAGO_ACCESS_TOKEN não configurado"}
    
    try:
        url = f"{MP_API_BASE}/v1/payments"
        
        # Calcula data de expiração
        expiracao = datetime.utcnow() + timedelta(minutes=expiracao_minutos)
        
        payload = {
            "transaction_amount": float(valor),
            "description": descricao,
            "payment_method_id": "pix",
            "payer": {
                "email": email_pagador
            },
            "date_of_expiration": expiracao.strftime("%Y-%m-%dT%H:%M:%S.000-03:00")
        }
        
        if external_reference:
            payload["external_reference"] = external_reference
        
        response = requests.post(url, json=payload, headers=get_headers(), timeout=30)
        
        if response.status_code in [200, 201]:
            data = response.json()
            
            # Extrai informações do PIX
            pix_info = data.get("point_of_interaction", {}).get("transaction_data", {})
            
            return {
                "success": True,
                "payment_id": data.get("id"),
                "status": data.get("status"),
                "qr_code": pix_info.get("qr_code"),  # Código copia-cola
                "qr_code_base64": pix_info.get("qr_code_base64"),  # Imagem em base64
                "ticket_url": pix_info.get("ticket_url"),  # URL para pagar
                "expiration": expiracao.isoformat()
            }
        else:
            error_data = response.json() if response.text else {}
            return {
                "success": False,
                "error": error_data.get("message", f"Erro HTTP {response.status_code}"),
                "details": error_data
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout na conexão com Mercado Pago"}
    except Exception as e:
        logger.error(f"Erro ao criar pagamento PIX: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# CONSULTAR STATUS DO PAGAMENTO
# ============================================================================

def consultar_pagamento(payment_id: str) -> Dict[str, Any]:
    """
    Consulta o status de um pagamento.
    
    Args:
        payment_id: ID do pagamento retornado ao criar
    
    Returns:
        Dict com status e detalhes do pagamento
    """
    
    if not MERCADO_PAGO_ACCESS_TOKEN:
        return {"success": False, "error": "Token não configurado"}
    
    try:
        url = f"{MP_API_BASE}/v1/payments/{payment_id}"
        response = requests.get(url, headers=get_headers(), timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "payment_id": data.get("id"),
                "status": data.get("status"),
                "status_detail": data.get("status_detail"),
                "amount": data.get("transaction_amount"),
                "date_approved": data.get("date_approved"),
                "external_reference": data.get("external_reference")
            }
        else:
            return {"success": False, "error": f"Erro HTTP {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# PROCESSAR WEBHOOK
# ============================================================================

def processar_webhook_mercadopago(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa notificação de webhook do Mercado Pago.
    
    O Mercado Pago envia webhooks para:
    - payment.created
    - payment.updated
    
    Args:
        data: Payload JSON recebido no webhook
    
    Returns:
        Dict com informações processadas do pagamento
    """
    
    try:
        action = data.get("action")
        payment_data = data.get("data", {})
        payment_id = payment_data.get("id")
        
        if not payment_id:
            return {"success": False, "error": "payment_id não encontrado no webhook"}
        
        # Consulta detalhes completos do pagamento
        payment_details = consultar_pagamento(str(payment_id))
        
        if payment_details.get("success"):
            status = payment_details.get("status")
            
            return {
                "success": True,
                "action": action,
                "payment_id": payment_id,
                "status": status,
                "is_approved": status == "approved",
                "amount": payment_details.get("amount"),
                "external_reference": payment_details.get("external_reference"),
                "date_approved": payment_details.get("date_approved")
            }
        else:
            return payment_details
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# TESTE LOCAL
# ============================================================================

if __name__ == "__main__":
    # Teste básico
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=== Teste Mercado Pago PIX ===")
    
    if not os.getenv("MERCADO_PAGO_ACCESS_TOKEN"):
        print("❌ MERCADO_PAGO_ACCESS_TOKEN não configurado no .env")
    else:
        print("✅ Token configurado")
        
        # Teste de criação de pagamento
        resultado = criar_pagamento_pix(
            valor=1.00,
            descricao="Teste de integração",
            external_reference="teste_123"
        )
        
        if resultado["success"]:
            print(f"✅ Pagamento criado: {resultado['payment_id']}")
            print(f"   QR Code: {resultado['qr_code'][:50]}...")
        else:
            print(f"❌ Erro: {resultado['error']}")
