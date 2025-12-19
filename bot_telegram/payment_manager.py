"""
Gerenciador de Pagamentos PIX - Multi-Provider
Permite trocar entre Mercado Pago e PagBank facilmente.
"""

import os
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class PaymentProvider(Enum):
    """Provedores de pagamento disponíveis"""
    MERCADO_PAGO = "mercadopago"
    PAGBANK = "pagbank"


# Provedor ativo (configurável via env var)
ACTIVE_PROVIDER = os.getenv("PAYMENT_PROVIDER", "mercadopago").lower()


def get_active_provider() -> PaymentProvider:
    """Retorna o provedor ativo baseado na configuração"""
    if ACTIVE_PROVIDER == "pagbank":
        return PaymentProvider.PAGBANK
    return PaymentProvider.MERCADO_PAGO


def criar_pagamento_pix(
    valor: float,
    descricao: str,
    external_reference: Optional[str] = None,
    expiracao_minutos: int = 30,
    provider: Optional[PaymentProvider] = None
) -> Dict[str, Any]:
    """
    Cria um pagamento PIX usando o provedor configurado ou especificado.
    
    Args:
        valor: Valor em reais
        descricao: Descrição do produto/serviço
        external_reference: ID externo para rastrear
        expiracao_minutos: Tempo até expirar
        provider: Provedor específico (opcional, usa o padrão se não informado)
    
    Returns:
        Dict com dados do pagamento criado
    """
    
    active = provider or get_active_provider()
    
    logger.info(f"Creating payment via {active.value}: R${valor:.2f}")
    
    if active == PaymentProvider.MERCADO_PAGO:
        from mercadopago_integration import criar_pagamento_pix as mp_criar
        resultado = mp_criar(
            valor=valor,
            descricao=descricao,
            external_reference=external_reference,
            expiracao_minutos=expiracao_minutos
        )
    elif active == PaymentProvider.PAGBANK:
        from pagbank_integration import criar_pagamento_pix_pagbank as pg_criar
        resultado = pg_criar(
            valor=valor,
            descricao=descricao,
            external_reference=external_reference,
            expiracao_minutos=expiracao_minutos
        )
    else:
        resultado = {"success": False, "error": f"Provedor desconhecido: {active}"}
    
    # Adiciona info do provedor usado
    resultado["provider"] = active.value
    
    return resultado


def criar_pagamento_com_fallback(
    valor: float,
    descricao: str,
    external_reference: Optional[str] = None,
    expiracao_minutos: int = 30
) -> Dict[str, Any]:
    """
    Cria pagamento com fallback automático.
    Se o provedor principal falhar, tenta o secundário.
    
    Args:
        valor: Valor em reais
        descricao: Descrição
        external_reference: ID externo
        expiracao_minutos: Tempo até expirar
    
    Returns:
        Dict com dados do pagamento
    """
    
    # Tenta provedor principal
    primary = get_active_provider()
    resultado = criar_pagamento_pix(
        valor=valor,
        descricao=descricao,
        external_reference=external_reference,
        expiracao_minutos=expiracao_minutos,
        provider=primary
    )
    
    if resultado.get("success"):
        logger.info(f"Payment created via primary provider: {primary.value}")
        return resultado
    
    # Fallback para outro provedor
    logger.warning(f"Primary provider {primary.value} failed: {resultado.get('error')}")
    
    secondary = PaymentProvider.PAGBANK if primary == PaymentProvider.MERCADO_PAGO else PaymentProvider.MERCADO_PAGO
    
    logger.info(f"Attempting fallback to {secondary.value}")
    
    resultado_fallback = criar_pagamento_pix(
        valor=valor,
        descricao=descricao,
        external_reference=external_reference,
        expiracao_minutos=expiracao_minutos,
        provider=secondary
    )
    
    if resultado_fallback.get("success"):
        logger.info(f"Payment created via fallback provider: {secondary.value}")
        resultado_fallback["fallback_used"] = True
    else:
        logger.error(f"Both providers failed!")
    
    return resultado_fallback


def consultar_pagamento(payment_id: str, provider: Optional[PaymentProvider] = None) -> Dict[str, Any]:
    """
    Consulta status de um pagamento.
    
    Args:
        payment_id: ID do pagamento
        provider: Provedor onde o pagamento foi criado
    
    Returns:
        Dict com status
    """
    
    active = provider or get_active_provider()
    
    if active == PaymentProvider.MERCADO_PAGO:
        from mercadopago_integration import consultar_pagamento as mp_consultar
        return mp_consultar(payment_id)
    elif active == PaymentProvider.PAGBANK:
        from pagbank_integration import consultar_pedido_pagbank as pg_consultar
        return pg_consultar(payment_id)
    else:
        return {"success": False, "error": f"Provedor desconhecido: {active}"}


def processar_webhook(data: Dict[str, Any], provider: PaymentProvider) -> Dict[str, Any]:
    """
    Processa webhook de um provedor específico.
    
    Args:
        data: Payload do webhook
        provider: Qual provedor enviou
    
    Returns:
        Dict com dados processados
    """
    
    if provider == PaymentProvider.MERCADO_PAGO:
        from mercadopago_integration import processar_webhook_mercadopago as mp_webhook
        return mp_webhook(data)
    elif provider == PaymentProvider.PAGBANK:
        from pagbank_integration import processar_webhook_pagbank as pg_webhook
        return pg_webhook(data)
    else:
        return {"success": False, "error": f"Provedor desconhecido: {provider}"}


# ============================================================================
# STATUS DOS PROVEDORES
# ============================================================================

def verificar_status_provedores() -> Dict[str, Any]:
    """
    Verifica se os provedores estão configurados corretamente.
    
    Returns:
        Dict com status de cada provedor
    """
    
    status = {
        "active_provider": ACTIVE_PROVIDER,
        "providers": {}
    }
    
    # Mercado Pago
    mp_token = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "")
    status["providers"]["mercadopago"] = {
        "configured": bool(mp_token),
        "token_preview": mp_token[:20] + "..." if mp_token else None
    }
    
    # PagBank
    pg_token = os.getenv("PAGBANK_TOKEN", "")
    status["providers"]["pagbank"] = {
        "configured": bool(pg_token),
        "token_preview": pg_token[:20] + "..." if pg_token else None
    }
    
    return status
