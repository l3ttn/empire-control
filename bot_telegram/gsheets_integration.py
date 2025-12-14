"""
Google Sheets Integration for Telegram Bot Sales
Registra vendas do bot automaticamente no Google Sheets
"""

import os
import json
from datetime import datetime
from typing import Optional
import logging

# Load .env at module import time
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# Lazy load gspread to avoid import errors if not installed
_gspread_client = None
_spreadsheet = None


def get_gsheets_client():
    """Conecta ao Google Sheets usando credenciais do arquivo JSON."""
    global _gspread_client
    
    if _gspread_client is not None:
        return _gspread_client
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        credentials_file = os.getenv("GSHEETS_CREDENTIALS_FILE", "gsheets_credentials.json")
        if not os.path.exists(credentials_file):
            logger.error(f"Credentials file not found: {credentials_file}")
            return None
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        credentials = Credentials.from_service_account_file(
            credentials_file,
            scopes=scopes
        )
        
        _gspread_client = gspread.authorize(credentials)
        logger.info("Google Sheets client initialized successfully")
        return _gspread_client
        
    except ImportError:
        logger.error("gspread not installed. Run: pip install gspread google-auth")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets client: {e}")
        return None


def get_spreadsheet():
    """Abre a planilha e garante que a aba VendasBot existe."""
    global _spreadsheet
    
    if _spreadsheet is not None:
        return _spreadsheet
    
    try:
        client = get_gsheets_client()
        if not client:
            return None
        
        spreadsheet_name = os.getenv("SPREADSHEET_NAME", "Strip")
        
        _spreadsheet = client.open(spreadsheet_name)
        
        # Garante que a aba VendasBot existe
        existing_sheets = [ws.title for ws in _spreadsheet.worksheets()]
        
        if "VendasBot" not in existing_sheets:
            ws = _spreadsheet.add_worksheet(title="VendasBot", rows=1000, cols=10)
            ws.append_row(["data", "client_id", "conteudo", "valor", "payment_id", "status"])
            logger.info("Created VendasBot worksheet with headers")
        
        return _spreadsheet
        
    except Exception as e:
        logger.error(f"Failed to open spreadsheet: {e}")
        return None


def registrar_venda_bot(
    client_id: str,
    conteudo: str,
    valor: float,
    payment_id: str,
    status: str = "CONCLUIDA"
) -> bool:
    """
    Registra uma venda do bot no Google Sheets.
    
    Args:
        client_id: Telegram user ID
        conteudo: Nome do conteudo/servico vendido
        valor: Valor em reais
        payment_id: ID do pagamento PIX
        status: Status do pagamento (default: CONCLUIDA)
    
    Returns:
        True se registrado com sucesso, False caso contrario
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            logger.warning("Could not connect to Google Sheets, sale not recorded")
            return False
        
        ws = spreadsheet.worksheet("VendasBot")
        
        # Adiciona nova linha
        ws.append_row([
            datetime.now().isoformat(),
            str(client_id),
            conteudo,
            float(valor),
            payment_id,
            status
        ], value_input_option='RAW')
        
        logger.info(f"Sale registered: {conteudo} - R$ {valor:.2f} for client {client_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to register sale in Google Sheets: {e}")
        return False


def carregar_vendas_bot() -> list:
    """
    Carrega todas as vendas do bot do Google Sheets.
    
    Returns:
        Lista de dicts com os dados das vendas
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return []
        
        ws = spreadsheet.worksheet("VendasBot")
        all_values = ws.get_all_values()
        
        if len(all_values) <= 1:  # So header ou vazio
            return []
        
        headers = all_values[0]
        vendas = []
        
        for row in all_values[1:]:
            if len(row) >= len(headers):
                venda = dict(zip(headers, row))
                # Converte valor para float
                try:
                    venda['valor'] = float(str(venda.get('valor', 0)).replace(',', '.'))
                except:
                    venda['valor'] = 0.0
                vendas.append(venda)
        
        return vendas
        
    except Exception as e:
        logger.error(f"Failed to load bot sales from Google Sheets: {e}")
        return []


# Test connection when run directly
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing Google Sheets connection...")
    spreadsheet = get_spreadsheet()
    
    if spreadsheet:
        print(f"Connected to: {spreadsheet.title}")
        print(f"Worksheets: {[ws.title for ws in spreadsheet.worksheets()]}")
        
        # Test registration
        success = registrar_venda_bot(
            client_id="TEST_USER",
            conteudo="Teste de Integracao",
            valor=0.01,
            payment_id="test_" + datetime.now().strftime("%Y%m%d%H%M%S")
        )
        
        if success:
            print("Test sale registered successfully!")
        else:
            print("Failed to register test sale")
    else:
        print("Failed to connect to Google Sheets")
