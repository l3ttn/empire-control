"""
Módulo de integração com PagBank (PagSeguro) para pagamentos PIX.
Gera QR Code PIX e recebe notificações via webhook.
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import base64

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Token do PagBank (obtido em https://developer.pagbank.com.br/)
PAGBANK_TOKEN = os.getenv("PAGBANK_TOKEN", "")

# URLs da API (Produção)
PAGBANK_API_BASE = "https://api.pagseguro.com"
# Para Sandbox: "https://sandbox.api.pagseguro.com"

# Headers padrão
def get_headers():
    return {
        "Authorization": f"Bearer {PAGBANK_TOKEN}",
        "Content-Type": "application/json",
        "x-api-version": "4.0"
    }


# ============================================================================
# CRIAR PAGAMENTO PIX
# ============================================================================

def criar_pagamento_pix_pagbank(
    valor: float,
    descricao: str,
    external_reference: Optional[str] = None,
    expiracao_minutos: int = 30
) -> Dict[str, Any]:
    """
    Cria um pagamento PIX no PagBank.
    
    Args:
        valor: Valor em reais (ex: 60.00)
        descricao: Descrição do produto/serviço
        external_reference: ID externo para rastrear
        expiracao_minutos: Tempo até o PIX expirar
    
    Returns:
        Dict com:
            - success: bool
            - payment_id: ID do pagamento (charge_id)
            - qr_code: String do código PIX copia-cola
            - qr_code_base64: Imagem do QR code em base64
            - error: mensagem de erro (se houver)
    """
    
    if not PAGBANK_TOKEN:
        return {"success": False, "error": "PAGBANK_TOKEN não configurado"}
    
    try:
        url = f"{PAGBANK_API_BASE}/orders"
        
        # Calcula data de expiração
        expiracao = datetime.utcnow() + timedelta(minutes=expiracao_minutos)
        
        # Valor em centavos
        valor_centavos = int(valor * 100)
        
        payload = {
            "reference_id": external_reference or f"ref_{int(datetime.utcnow().timestamp())}",
            "customer": {
                "name": "Cliente Bot",
                "email": "cliente@bot.com",
                "tax_id": "00000000000"  # CPF genérico (PagBank aceita para PIX)
            },
            "items": [
                {
                    "reference_id": "item_1",
                    "name": descricao[:64],  # Max 64 chars
                    "quantity": 1,
                    "unit_amount": valor_centavos
                }
            ],
            "qr_codes": [
                {
                    "amount": {
                        "value": valor_centavos
                    },
                    "expiration_date": expiracao.strftime("%Y-%m-%dT%H:%M:%S-03:00")
                }
            ],
            "notification_urls": [
                os.getenv("PAGBANK_WEBHOOK_URL", "https://seu-app.com/webhook/pagbank")
            ]
        }
        
        response = requests.post(url, json=payload, headers=get_headers(), timeout=30)
        
        if response.status_code in [200, 201]:
            data = response.json()
            
            # Extrai informações do PIX
            qr_codes = data.get("qr_codes", [])
            if qr_codes:
                qr_data = qr_codes[0]
                qr_code_text = qr_data.get("text", "")  # Código copia-cola
                
                # PagBank retorna links para imagem do QR
                links = qr_data.get("links", [])
                qr_image_url = None
                for link in links:
                    if link.get("rel") == "QRCODE.PNG":
                        qr_image_url = link.get("href")
                        break
                
                # Baixar imagem e converter para base64
                qr_code_base64 = None
                if qr_image_url:
                    try:
                        img_response = requests.get(qr_image_url, timeout=10)
                        if img_response.status_code == 200:
                            qr_code_base64 = base64.b64encode(img_response.content).decode('utf-8')
                    except:
                        pass
                
                return {
                    "success": True,
                    "payment_id": data.get("id"),
                    "status": data.get("status", "pending"),
                    "qr_code": qr_code_text,
                    "qr_code_base64": qr_code_base64,
                    "qr_code_url": qr_image_url,
                    "expiration": expiracao.isoformat()
                }
            else:
                return {"success": False, "error": "QR Code não retornado pela API"}
        else:
            error_data = response.json() if response.text else {}
            error_messages = error_data.get("error_messages", [])
            error_msg = error_messages[0].get("description") if error_messages else f"Erro HTTP {response.status_code}"
            return {
                "success": False,
                "error": error_msg,
                "details": error_data
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout na conexão com PagBank"}
    except Exception as e:
        logger.error(f"Erro ao criar pagamento PIX PagBank: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# CONSULTAR STATUS DO PEDIDO
# ============================================================================

def consultar_pedido_pagbank(order_id: str) -> Dict[str, Any]:
    """
    Consulta o status de um pedido/pagamento.
    
    Args:
        order_id: ID do pedido retornado ao criar
    
    Returns:
        Dict com status e detalhes do pagamento
    """
    
    if not PAGBANK_TOKEN:
        return {"success": False, "error": "Token não configurado"}
    
    try:
        url = f"{PAGBANK_API_BASE}/orders/{order_id}"
        response = requests.get(url, headers=get_headers(), timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar status dos charges (pagamentos)
            charges = data.get("charges", [])
            is_paid = False
            paid_amount = 0
            
            for charge in charges:
                if charge.get("status") == "PAID":
                    is_paid = True
                    paid_amount = charge.get("amount", {}).get("value", 0) / 100
            
            return {
                "success": True,
                "order_id": data.get("id"),
                "reference_id": data.get("reference_id"),
                "status": "PAID" if is_paid else data.get("status", "PENDING"),
                "is_paid": is_paid,
                "amount": paid_amount,
            }
        else:
            return {"success": False, "error": f"Erro HTTP {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# PROCESSAR WEBHOOK
# ============================================================================

def processar_webhook_pagbank(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa notificação de webhook do PagBank.
    
    O PagBank envia webhooks para mudanças de status.
    
    Args:
        data: Payload JSON recebido no webhook
    
    Returns:
        Dict com informações processadas do pagamento
    """
    
    try:
        # PagBank envia notificações com diferentes estruturas
        # Pode ser notificação de charge ou order
        
        charges = data.get("charges", [])
        order_id = data.get("id")
        reference_id = data.get("reference_id")
        
        for charge in charges:
            status = charge.get("status")
            
            if status == "PAID":
                paid_at = charge.get("paid_at")
                amount = charge.get("amount", {}).get("value", 0) / 100
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "reference_id": reference_id,
                    "status": "PAID",
                    "is_approved": True,
                    "amount": amount,
                    "paid_at": paid_at
                }
        
        # Não é pagamento aprovado
        return {
            "success": True,
            "order_id": order_id,
            "status": data.get("status", "UNKNOWN"),
            "is_approved": False
        }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# TESTE LOCAL
# ============================================================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=== Teste PagBank PIX ===")
    
    if not os.getenv("PAGBANK_TOKEN"):
        print("❌ PAGBANK_TOKEN não configurado no .env")
    else:
        print("✅ Token configurado")
        
        # Teste de criação de pagamento
        resultado = criar_pagamento_pix_pagbank(
            valor=1.00,
            descricao="Teste de integração",
            external_reference="teste_123"
        )
        
        if resultado["success"]:
            print(f"✅ Pagamento criado: {resultado['payment_id']}")
            print(f"   QR Code: {resultado['qr_code'][:50] if resultado.get('qr_code') else 'N/A'}...")
        else:
            print(f"❌ Erro: {resultado['error']}")
