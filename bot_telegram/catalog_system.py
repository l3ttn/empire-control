# =============================================================================
# CATÁLOGO DE CONTEÚDOS - SISTEMA DE VENDA DE VÍDEOS E FOTOS
# =============================================================================

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# =============================================================================
# CONFIGURAÇÃO DO CATÁLOGO
# =============================================================================

CATALOG_FILE = 'catalog_data.json'
PURCHASES_FILE = 'purchases_data.json'

# Estrutura do catálogo:
# {
#     "content_id": {
#         "title": "Título do conteúdo",
#         "description": "Descrição detalhada",
#         "category": "solo|duo|fetiche|personalizados|outros",
#         "content_type": "video|photo_pack",
#         "price": 50.00,
#         "preview_file_id": "telegram_file_id_da_preview",  # GIF ou foto de capa
#         "content_file_ids": ["file_id_1", "file_id_2"],  # IDs dos arquivos completos
#         "duration": "5 min",  # Para vídeos
#         "quantity": 10,  # Para packs de fotos
#         "created_at": "2025-10-20T10:30:00",
#         "active": True
#     }
# }

# Estrutura de compras:
# {
#     "purchase_id": {
#         "user_id": 123456,
#         "content_id": "content_123",
#         "payment_id": "pix_payment_id",
#         "amount": 50.00,
#         "status": "pending|completed|cancelled",
#         "purchased_at": "2025-10-20T10:30:00",
#         "delivered": False
#     }
# }

# =============================================================================
# FUNÇÕES DE PERSISTÊNCIA
# =============================================================================

def load_catalog() -> Dict[str, Dict[str, Any]]:
    """Carrega catálogo do arquivo JSON"""
    if os.path.exists(CATALOG_FILE):
        try:
            with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar catálogo: {e}")
            return {}
    return {}

def save_catalog(catalog: Dict[str, Dict[str, Any]]) -> None:
    """Salva catálogo no arquivo JSON"""
    try:
        with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar catálogo: {e}")

def load_purchases() -> Dict[str, Dict[str, Any]]:
    """Carrega histórico de compras do arquivo JSON"""
    if os.path.exists(PURCHASES_FILE):
        try:
            with open(PURCHASES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar compras: {e}")
            return {}
    return {}

def save_purchases(purchases: Dict[str, Dict[str, Any]]) -> None:
    """Salva histórico de compras no arquivo JSON"""
    try:
        with open(PURCHASES_FILE, 'w', encoding='utf-8') as f:
            json.dump(purchases, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar compras: {e}")

# =============================================================================
# FUNÇÕES DE GERENCIAMENTO DO CATÁLOGO
# =============================================================================

def add_content(content_data: Dict[str, Any]) -> str:
    """Adiciona novo conteúdo ao catálogo"""
    catalog = load_catalog()
    
    # Gerar ID único
    content_id = f"content_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Adicionar timestamp e status
    content_data['created_at'] = datetime.now().isoformat()
    content_data['active'] = True
    
    catalog[content_id] = content_data
    save_catalog(catalog)
    
    return content_id

def update_content(content_id: str, updates: Dict[str, Any]) -> bool:
    """Atualiza conteúdo existente"""
    catalog = load_catalog()
    
    if content_id not in catalog:
        return False
    
    catalog[content_id].update(updates)
    save_catalog(catalog)
    
    return True

def delete_content(content_id: str) -> bool:
    """Remove conteúdo do catálogo (soft delete - marca como inativo)"""
    catalog = load_catalog()
    
    if content_id not in catalog:
        return False
    
    catalog[content_id]['active'] = False
    save_catalog(catalog)
    
    return True

def get_content(content_id: str) -> Optional[Dict[str, Any]]:
    """Retorna dados de um conteúdo específico"""
    catalog = load_catalog()
    return catalog.get(content_id)

def get_contents_by_category(category: str) -> List[Dict[str, Any]]:
    """Retorna todos os conteúdos ativos de uma categoria"""
    catalog = load_catalog()
    
    return [
        {"id": cid, **cdata}
        for cid, cdata in catalog.items()
        if cdata.get('active', True) and cdata.get('category') == category
    ]

def get_all_active_contents() -> List[Dict[str, Any]]:
    """Retorna todos os conteúdos ativos"""
    catalog = load_catalog()
    
    return [
        {"id": cid, **cdata}
        for cid, cdata in catalog.items()
        if cdata.get('active', True)
    ]

# =============================================================================
# FUNÇÕES DE GERENCIAMENTO DE COMPRAS
# =============================================================================

def create_purchase(user_id: int, content_id: str, payment_id: str, amount: float) -> str:
    """Cria registro de compra"""
    purchases = load_purchases()
    
    purchase_id = f"purchase_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
    
    purchases[purchase_id] = {
        'user_id': user_id,
        'content_id': content_id,
        'payment_id': payment_id,
        'amount': amount,
        'status': 'pending',
        'purchased_at': datetime.now().isoformat(),
        'delivered': False
    }
    
    save_purchases(purchases)
    return purchase_id

def mark_purchase_completed(payment_id: str) -> Optional[Dict[str, Any]]:
    """Marca compra como completa pelo payment_id"""
    purchases = load_purchases()
    
    for purchase_id, purchase_data in purchases.items():
        if purchase_data['payment_id'] == payment_id:
            purchase_data['status'] = 'completed'
            save_purchases(purchases)
            return purchase_data
    
    return None

def mark_purchase_delivered(purchase_id: str) -> bool:
    """Marca conteúdo como entregue"""
    purchases = load_purchases()
    
    if purchase_id not in purchases:
        return False
    
    purchases[purchase_id]['delivered'] = True
    save_purchases(purchases)
    
    return True

def get_user_purchases(user_id: int) -> List[Dict[str, Any]]:
    """Retorna todas as compras de um usuário"""
    purchases = load_purchases()
    
    return [
        {"id": pid, **pdata}
        for pid, pdata in purchases.items()
        if pdata['user_id'] == user_id
    ]

def get_purchase_by_payment_id(payment_id: str) -> Optional[Dict[str, Any]]:
    """Busca compra pelo payment_id"""
    purchases = load_purchases()
    
    for purchase_id, purchase_data in purchases.items():
        if purchase_data['payment_id'] == payment_id:
            return {"id": purchase_id, **purchase_data}
    
    return None

# =============================================================================
# CATEGORIAS DISPONÍVEIS
# =============================================================================

CATEGORIES = {
    "solo": {
        "name": "Solo",
        "emoji": "💋",
        "description": "Conteúdos solo exclusivos"
    },
    "duo": {
        "name": "Duo/Grupo",
        "emoji": "👯",
        "description": "Conteúdos com outras modelos"
    },
    "fetiche": {
        "name": "Fetiche",
        "emoji": "🔥",
        "description": "Conteúdos de fetiche específicos"
    },
    "personalizados": {
        "name": "Personalizados",
        "emoji": "⭐",
        "description": "Conteúdos feitos sob encomenda"
    },
    "outros": {
        "name": "Outros",
        "emoji": "📹",
        "description": "Outros conteúdos exclusivos"
    }
}

def get_category_info(category_key: str) -> Optional[Dict[str, str]]:
    """Retorna informações de uma categoria"""
    return CATEGORIES.get(category_key)

