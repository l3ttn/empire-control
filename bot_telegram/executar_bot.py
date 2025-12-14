#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Execução do Bot Telegram
Executa o bot com verificações de segurança
"""

import os
import sys
import subprocess
from pathlib import Path

def verificar_arquivo_env():
    """Verifica se o arquivo .env existe e está configurado"""
    if not os.path.exists('.env'):
        print("ERRO - Arquivo .env nao encontrado")
        print("Execute: python configurar_bot.py")
        return False
    
    return True

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print("Verificando dependencias...")
    
    try:
        import telegram
        print("OK - python-telegram-bot instalado")
    except ImportError:
        print("ERRO - python-telegram-bot nao instalado")
        print("Execute: pip install python-telegram-bot==20.7")
        return False
    
    try:
        import requests
        print("OK - requests instalado")
    except ImportError:
        print("ERRO - requests nao instalado")
        print("Execute: pip install requests==2.31.0")
        return False
    
    return True

def carregar_variaveis_ambiente():
    """Carrega as variáveis de ambiente do arquivo .env"""
    if not os.path.exists('.env'):
        return False
    
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith('#') and '=' in linha:
                    chave, valor = linha.split('=', 1)
                    os.environ[chave.strip()] = valor.strip()
        return True
    except Exception as e:
        print(f"ERRO - Erro ao carregar .env: {e}")
        return False

def verificar_configuracao():
    """Verifica se a configuração está completa"""
    variaveis_necessarias = [
        'TELEGRAM_BOT_TOKEN',
        'LIVEPIX_API_KEY',
        'LIVEPIX_WEBHOOK_SECRET',
        'TELEGRAM_CHANNEL_ID',
        'TELEGRAM_ADMIN_ID'
    ]
    
    faltando = []
    for var in variaveis_necessarias:
        if not os.getenv(var):
            faltando.append(var)
    
    if faltando:
        print(f"ERRO - Variaveis faltando: {', '.join(faltando)}")
        print("Configure no arquivo .env e execute novamente")
        return False
    
    print("OK - Configuracao completa")
    return True

def executar_bot():
    """Executa o bot"""
    print("\n=== EXECUTANDO BOT TELEGRAM ===")
    print("Pressione Ctrl+C para parar o bot")
    print()
    
    try:
        # Executa o bot
        subprocess.run([sys.executable, 'bot.py'], check=True)
    except KeyboardInterrupt:
        print("\nBot parado pelo usuario")
    except subprocess.CalledProcessError as e:
        print(f"ERRO - Bot falhou com codigo {e.returncode}")
        return False
    except Exception as e:
        print(f"ERRO - Erro ao executar bot: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("EXECUTOR DO BOT TELEGRAM")
    print("=" * 30)
    
    # Verifica arquivo .env
    if not verificar_arquivo_env():
        return False
    
    # Verifica dependências
    if not verificar_dependencias():
        return False
    
    # Carrega variáveis de ambiente
    if not carregar_variaveis_ambiente():
        return False
    
    # Verifica configuração
    if not verificar_configuracao():
        return False
    
    # Executa o bot
    return executar_bot()

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
