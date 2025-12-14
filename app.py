"""
EMPIRE CONTROL - Financial Dashboard
=====================================
Sistema de controle financeiro centralizado integrando:
- Revenue API (Revenue Tracking)
- Inventory CSV (Stock Sales)
- Household Expenses (Split 50/50)

Linguagem da Interface: PORTUGUES (PT-BR)
Framework: Streamlit + Pandas + Plotly + Requests
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os
import requests
import re
import json
import pickle
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import time
from playwright.sync_api import sync_playwright
import asyncio

# ==================== CONFIGURACAO DA PAGINA ====================
st.set_page_config(
    page_title="Empire Control",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS DARK MODE HACKER/TRADER ====================
st.markdown("""
<style>
    /* DARK HACKER THEME */
    .stApp {
        background: #0a0a0a !important;
    }

    section[data-testid="stSidebar"] {
        background: #111111 !important;
    }

    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    .stApp, .stApp * {
        color: #ffffff !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 5px;
        gap: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #888888 !important;
        border-radius: 8px;
        padding: 10px 20px;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #2a2a2a;
        color: #00ff88 !important;
        font-weight: bold;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%) !important;
        color: #000000 !important;
        border: none;
        font-weight: bold;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
    }

    .stButton > button[kind="secondary"] {
        background: #333333 !important;
        color: #ffffff !important;
        border: 1px solid #444444;
    }

    /* DataFrames */
    .stDataFrame {
        background: #1a1a1a;
        border-radius: 10px;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
    }

    [data-testid="stMetricLabel"] {
        color: #888888 !important;
        text-transform: uppercase;
        font-size: 0.85rem !important;
    }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid #2a2a2a;
        margin: 8px 0;
        transition: all 0.3s ease;
    }

    .kpi-card:hover {
        border-color: #00ff88;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
    }

    .kpi-title {
        color: #888888 !important;
        font-size: 0.85rem;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 500;
    }

    .kpi-value-green {
        color: #00ff88 !important;
        font-size: 2rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }

    .kpi-value-red {
        color: #ff4444 !important;
        font-size: 2rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
    }

    .kpi-value-gold {
        color: #ffd700 !important;
        font-size: 2rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }

    .kpi-value-blue {
        color: #4da6ff !important;
        font-size: 2rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(77, 166, 255, 0.5);
    }

    .kpi-value-purple {
        color: #b366ff !important;
        font-size: 2rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(179, 102, 255, 0.5);
    }

    .neon-green {
        color: #00ff88 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.8);
    }

    .neon-red {
        color: #ff4444 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 20px rgba(255, 68, 68, 0.8);
    }

    /* Success/Warning Boxes */
    .success-box {
        background: #0a0a0a;
        border: 2px solid #00ff88;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin: 16px 0;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.2);
    }

    .warning-box {
        background: #0a0a0a;
        border: 2px solid #ff4444;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin: 16px 0;
        box-shadow: 0 0 30px rgba(255, 68, 68, 0.2);
    }

    .info-box {
        background: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 16px 0;
    }

    /* Main Header */
    .main-header {
        text-align: center;
        padding: 40px;
        background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
        border-radius: 16px;
        margin-bottom: 24px;
        border: 2px solid #00ff88;
        box-shadow: 0 0 40px rgba(0, 255, 136, 0.2);
    }

    .main-header h1 {
        color: #00ff88 !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
    }

    .main-header p {
        color: #888888 !important;
        margin: 8px 0 0 0;
    }

    /* User Badge */
    .user-badge {
        background: #1a1a1a;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 12px 0;
        border: 1px solid #333333;
    }

    /* Settlement Box */
    .settlement-box {
        background: #1a1a1a;
        border: 2px solid #ffd700;
        border-radius: 12px;
        padding: 28px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.2);
    }

    /* Big Metric */
    .big-metric {
        background: #0a0a0a;
        border: 2px solid #00ff88;
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 0 40px rgba(0, 255, 136, 0.2);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }

    .stSelectbox > div > div {
        background-color: #1a1a1a !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }

    .stDateInput > div > div > input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }

    /* File Uploader */
    .stFileUploader > div {
        background-color: #1a1a1a !important;
        border: 2px dashed #333 !important;
        border-radius: 12px !important;
    }

    .stFileUploader label {
        color: #888888 !important;
    }

    /* Dropdown menus */
    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background-color: #1a1a1a !important;
    }

    [data-baseweb="menu"] li {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }

    [data-baseweb="menu"] li:hover {
        background-color: #2a2a2a !important;
    }

    /* Form container */
    [data-testid="stForm"] {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }

    /* Alert boxes */
    .stAlert {
        background: #1a1a1a !important;
        border: 1px solid #333333;
    }

    hr {
        border-color: #2a2a2a !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== PATHS ====================
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DESPESAS_FILE = os.path.join(DATA_DIR, "despesas.csv")
COOKIES_FILE = os.path.join(DATA_DIR, "stipchat_cookies.pkl")
PRODUTOS_FILE = os.path.join(DATA_DIR, "produtos.json")
VENDAS_FILE = os.path.join(DATA_DIR, "vendas.json")

# ==================== UTILITY FUNCTIONS ====================

def limpar_currency_br(valor_str):
    """
    Limpa valores monetarios brasileiros e converte para float.
    Exemplo: "R$ 1.234,56" -> 1234.56
    """
    try:
        if pd.isna(valor_str) or valor_str == '':
            return 0.0

        # Remove "R$" e espacos
        limpo = str(valor_str).replace('R$', '').strip()
        # Remove pontos (separador de milhar)
        limpo = limpo.replace('.', '')
        # Substitui virgula por ponto (separador decimal)
        limpo = limpo.replace(',', '.')

        return float(limpo)
    except:
        return 0.0


def salvar_cookies(driver, filepath):
    """Salva cookies do driver em arquivo."""
    cookies = driver.get_cookies()
    with open(filepath, 'wb') as f:
        pickle.dump(cookies, f)


def carregar_cookies(driver, filepath):
    """Carrega cookies do arquivo para o driver."""
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    pass
        return True
    return False


def inject_advanced_fingerprint_spoofing(driver):
    """
    Injeta fingerprint completo com noise reduction - bypassa deteccao avancada.
    """
    # Canvas fingerprint com noise
    canvas_script = """
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;

    const noise = () => Math.random() * 0.0001;

    HTMLCanvasElement.prototype.toDataURL = function() {
        const context = this.getContext('2d');
        const imageData = context.getImageData(0, 0, this.width, this.height);
        for (let i = 0; i < imageData.data.length; i += 4) {
            imageData.data[i] += noise();
            imageData.data[i + 1] += noise();
            imageData.data[i + 2] += noise();
        }
        context.putImageData(imageData, 0, 0);
        return originalToDataURL.apply(this, arguments);
    };
    """

    # WebGL fingerprint com GPU real (Intel Iris)
    webgl_script = """
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Inc.';
        }
        if (parameter === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter.apply(this, arguments);
    };

    const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
    WebGL2RenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Inc.';
        }
        if (parameter === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter2.apply(this, arguments);
    };
    """

    # Plugins reais
    plugins_script = """
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {
                name: 'Chrome PDF Plugin',
                filename: 'internal-pdf-viewer',
                description: 'Portable Document Format'
            },
            {
                name: 'Chrome PDF Viewer',
                filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                description: ''
            },
            {
                name: 'Native Client',
                filename: 'internal-nacl-plugin',
                description: ''
            }
        ]
    });
    """

    # Hardware concurrency randomizado
    hardware_script = f"""
    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: () => {random.choice([4, 8, 12, 16])}
    }});
    """

    # Device memory
    memory_script = f"""
    Object.defineProperty(navigator, 'deviceMemory', {{
        get: () => {random.choice([4, 8, 16])}
    }});
    """

    # Screen resolution com noise
    screen_script = f"""
    Object.defineProperty(screen, 'width', {{
        get: () => {random.randint(1920, 2560)}
    }});
    Object.defineProperty(screen, 'height', {{
        get: () => {random.randint(1080, 1440)}
    }});
    Object.defineProperty(screen, 'availWidth', {{
        get: () => screen.width
    }});
    Object.defineProperty(screen, 'availHeight', {{
        get: () => screen.height - 40
    }});
    """

    # Permissions
    permissions_script = """
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    """

    # Battery API
    battery_script = """
    Object.defineProperty(navigator, 'getBattery', {
        get: () => () => Promise.resolve({
            charging: true,
            chargingTime: 0,
            dischargingTime: Infinity,
            level: 1
        })
    });
    """

    # Audio context fingerprint com noise
    audio_script = """
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const originalGetChannelData = AudioBuffer.prototype.getChannelData;
    AudioBuffer.prototype.getChannelData = function() {
        const data = originalGetChannelData.apply(this, arguments);
        for (let i = 0; i < data.length; i++) {
            data[i] += Math.random() * 0.0001;
        }
        return data;
    };
    """

    # Timezone consistente
    timezone_script = """
    Date.prototype.getTimezoneOffset = function() {
        return 180; // America/Sao_Paulo
    };
    """

    # Executa todos os scripts
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': canvas_script})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': webgl_script})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': plugins_script})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': hardware_script})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': memory_script})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': screen_script})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': permissions_script})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': battery_script})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': audio_script})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': timezone_script})
    except:
        pass


def fazer_login_playwright_stealth():
    """
    PLAYWRIGHT - Motor de automacao ENTERPRISE com evasao maxima.
    Playwright nao deixa marcas de WebDriver, mais dificil de detectar que Selenium.
    """
    try:
        # Fix asyncio no Windows - requer ProactorEventLoop
        import sys
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        with sync_playwright() as p:
            # Lanca Chromium com flags de evasao
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                ],
                channel='chrome'  # Usa Chrome instalado ao inves de Chromium
            )

            # Cria contexto com fingerprint real
            context = browser.new_context(
                viewport={'width': random.randint(1920, 2560), 'height': random.randint(1080, 1440)},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                locale='pt-BR',
                timezone_id='America/Sao_Paulo',
                permissions=['geolocation', 'notifications'],
                geolocation={'latitude': -23.5505, 'longitude': -46.6333},  # Sao Paulo
                color_scheme='dark',
                device_scale_factor=1,
                has_touch=False,
                is_mobile=False,
            )

            # Injeta scripts de evasao avancada via CDP
            page = context.new_page()

            # Script de evasao completa - oculta Playwright
            evasion_script = """
            // Remove navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Chrome com plugins reais
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        name: 'Chrome PDF Plugin',
                        filename: 'internal-pdf-viewer',
                        description: 'Portable Document Format'
                    },
                    {
                        name: 'Chrome PDF Viewer',
                        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                        description: ''
                    },
                    {
                        name: 'Native Client',
                        filename: 'internal-nacl-plugin',
                        description: ''
                    }
                ]
            });

            // WebGL com GPU real (Intel Iris)
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                return getParameter.apply(this, arguments);
            };

            const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                return getParameter2.apply(this, arguments);
            };

            // Canvas com noise
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const noise = () => Math.random() * 0.0001;
            HTMLCanvasElement.prototype.toDataURL = function() {
                const context = this.getContext('2d');
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] += noise();
                    imageData.data[i + 1] += noise();
                    imageData.data[i + 2] += noise();
                }
                context.putImageData(imageData, 0, 0);
                return originalToDataURL.apply(this, arguments);
            };

            // Hardware randomizado
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => """ + str(random.choice([8, 12, 16])) + """
            });

            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => """ + str(random.choice([8, 16])) + """
            });

            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // Chrome runtime
            window.chrome = {
                runtime: {}
            };

            // Languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
            """

            # Adiciona script antes de qualquer navegacao
            page.add_init_script(evasion_script)

            def human_delay(min_sec=2, max_sec=5):
                time.sleep(random.uniform(min_sec, max_sec))

            # Navega para homepage com timing humano
            page.goto('https://br.platform.com', wait_until='networkidle')
            human_delay(3, 6)

            # Scroll aleatorio (simula leitura)
            page.evaluate(f"window.scrollTo(0, {random.randint(100, 400)})")
            human_delay(1, 2)

            # Movimento de mouse aleatorio (comportamento humano)
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                page.mouse.move(x, y)
                time.sleep(random.uniform(0.5, 1.5))

            st.success("Navegador Playwright aberto. Faca login manualmente e aguarde...")
            st.info("Apos fazer login, aguarde 30 segundos para os cookies serem salvos automaticamente.")

            # Aguarda 90 segundos para usuario fazer login
            for i in range(90):
                time.sleep(1)
                if i % 10 == 0:
                    st.write(f"Aguardando login... {90-i}s restantes")

            # Salva cookies do contexto
            cookies = context.cookies()

            # Converte cookies do Playwright para formato Selenium/pickle
            selenium_cookies = []
            for cookie in cookies:
                selenium_cookie = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie.get('domain', ''),
                    'path': cookie.get('path', '/'),
                    'secure': cookie.get('secure', False),
                    'httpOnly': cookie.get('httpOnly', False),
                    'sameSite': cookie.get('sameSite', 'Lax'),
                }
                if 'expires' in cookie:
                    selenium_cookie['expiry'] = int(cookie['expires'])
                selenium_cookies.append(selenium_cookie)

            with open(COOKIES_FILE, 'wb') as f:
                pickle.dump(selenium_cookies, f)

            st.success(f"Cookies salvos com sucesso! Total: {len(selenium_cookies)} cookies")

            browser.close()

            return {'success': True, 'cookies_count': len(selenium_cookies)}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def fazer_login_interativo():
    """
    Perfil temporário persistente - mais estável que perfil real.
    """
    try:
        # Cria diretório de perfil temporário persistente
        temp_profile = os.path.join(DATA_DIR, "chrome_temp_profile")
        if not os.path.exists(temp_profile):
            os.makedirs(temp_profile)

        # Chrome SIMPLES - sem firulas que causam crash
        options = Options()

        # Perfil temporário dedicado
        options.add_argument(f"user-data-dir={temp_profile}")

        # Flags MÍNIMAS anti-detecção
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Desabilita verificações de segurança excessivas
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')

        # Ignora erros de certificado
        options.add_argument('--ignore-certificate-errors')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Só stealth básico (sem injeção complexa que causa crash)
        stealth(driver,
            languages=["pt-BR", "pt", "en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        # Delays MUITO humanos
        def human_delay(min_sec=2, max_sec=5):
            time.sleep(random.uniform(min_sec, max_sec))

        try:
            # Vai para homepage primeiro (comportamento humano)
            driver.get('https://br.platform.com')
            human_delay(3, 6)

            # Scroll aleatorio (simula leitura)
            driver.execute_script(f"window.scrollTo(0, {random.randint(100, 300)})")
            human_delay(1, 2)

            # Agora vai para login
            driver.get('https://br.platform.com/login')
            human_delay(2, 4)

            st.info("Navegador aberto! Faca login manualmente e marque 'Confiar neste dispositivo'. Aguardando...")

            # Aguarda usuario fazer login
            WebDriverWait(driver, 300).until(
                lambda d: 'earnings' in d.current_url or d.current_url == 'https://br.platform.com/'
            )

            # Usuario logou! Salvar cookies
            salvar_cookies(driver, COOKIES_FILE)
            human_delay(2, 4)

            # Vai para página de earnings
            driver.get('https://br.platform.com/earnings/tokens-history')
            human_delay(5, 8)

            # Extrai dados via JavaScript
            script = """
            return fetch('https://br.platform.com/api/front/v3/config/initial?requestPath=%2Fearnings%2Ftokens-history')
                .then(r => r.json())
                .then(d => d);
            """

            data = driver.execute_script(script)

            if data and 'initial' in data:
                user_data = data.get('initial', {}).get('client', {}).get('user', {})
                tokens = user_data.get('tokens', 0)

                return {
                    'success': True,
                    'tokens': tokens,
                    'secondsOnline': 0,
                    'username': user_data.get('username', ''),
                    'data': data
                }
            else:
                return {'success': False, 'error': 'Nao foi possivel extrair dados'}

        finally:
            driver.quit()

    except Exception as e:
        return {'success': False, 'error': f'Erro: {str(e)}'}


def fetch_stipchat_stats_com_cookies_salvos():
    """
    Usa cookies salvos anteriormente com anti-deteccao (headless).
    """
    try:
        if not os.path.exists(COOKIES_FILE):
            return {'success': False, 'error': 'Cookies nao encontrados. Faca login interativo primeiro.'}

        # Chrome headless com stealth
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # INJETA FINGERPRINT COMPLETO COM NOISE
        inject_advanced_fingerprint_spoofing(driver)

        # Aplica stealth
        stealth(driver,
            languages=["pt-BR", "pt", "en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        try:
            # Vai para site primeiro
            driver.get('https://br.platform.com')
            time.sleep(random.uniform(2, 4))

            # Carrega cookies salvos
            carregar_cookies(driver, COOKIES_FILE)

            # Vai para página de earnings
            driver.get('https://br.platform.com/earnings/tokens-history')
            time.sleep(random.uniform(4, 6))

            # Extrai dados via JavaScript
            script = """
            return fetch('https://br.platform.com/api/front/v3/config/initial?requestPath=%2Fearnings%2Ftokens-history')
                .then(r => r.json())
                .then(d => d);
            """

            data = driver.execute_script(script)

            if data and 'initial' in data:
                user_data = data.get('initial', {}).get('client', {}).get('user', {})

                if not user_data:
                    return {'success': False, 'error': 'Cookies expiraram. Faca login interativo novamente.'}

                tokens = user_data.get('tokens', 0)

                return {
                    'success': True,
                    'tokens': tokens,
                    'secondsOnline': 0,
                    'username': user_data.get('username', ''),
                    'data': data
                }
            else:
                return {'success': False, 'error': 'Nao foi possivel extrair dados'}

        finally:
            driver.quit()

    except Exception as e:
        return {'success': False, 'error': f'Erro: {str(e)}'}


def fetch_stipchat_stats_selenium(username, password):
    """
    Usa Selenium para fazer scraping direto da pagina de earnings.
    Login automatico + extracao de dados.
    """
    try:
        # Configurar Chrome headless
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Iniciar driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            # Acessa página de login
            driver.get('https://br.platform.com/login')
            time.sleep(3)

            # Faz login
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = driver.find_element(By.NAME, "password")

            username_field.send_keys(username)
            password_field.send_keys(password)

            # Clica no botão de login
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()

            time.sleep(5)  # Aguarda login processar

            # Intercepta requisições de rede via CDP
            driver.execute_cdp_cmd('Network.enable', {})

            # Vai para página de earnings
            driver.get('https://br.platform.com/earnings/tokens-history')
            time.sleep(5)

            # Captura dados via JavaScript
            script = """
            return fetch('https://br.platform.com/api/front/v3/config/initial?requestPath=%2Fearnings%2Ftokens-history')
                .then(r => r.json())
                .then(d => d);
            """

            data = driver.execute_script(script)

            if data and 'initial' in data:
                user_data = data.get('initial', {}).get('client', {}).get('user', {})
                tokens = user_data.get('tokens', 0)

                return {
                    'success': True,
                    'tokens': tokens,
                    'secondsOnline': 0,
                    'username': user_data.get('username', ''),
                    'data': data
                }
            else:
                return {'success': False, 'error': 'Nao foi possivel extrair dados'}

        finally:
            driver.quit()

    except Exception as e:
        return {'success': False, 'error': f'Erro no Selenium: {str(e)}'}


def fetch_stipchat_stats_requests(session_key, all_cookies=None):
    """
    Usa requests com TODOS os cookies do browser.
    """
    try:
        url = "https://br.platform.com/api/front/v3/config/initial"

        params = {'requestPath': '/earnings/tokens-history'}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://br.platform.com/earnings/tokens-history',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }

        # Usa todos os cookies se fornecidos
        if all_cookies:
            cookies = all_cookies
        else:
            cookies = {
                'platform_com_sessionId': session_key,
                'localeDomain': 'br'
            }

        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=10)

        if response.status_code == 200:
            try:
                data = response.json()
                user_data = data.get('initial', {}).get('client', {}).get('user', {})

                if not user_data:
                    return {'success': False, 'error': 'Usuario nao encontrado. Cookie invalido.'}

                return {
                    'success': True,
                    'tokens': user_data.get('tokens', 0),
                    'secondsOnline': 0,
                    'username': user_data.get('username', ''),
                    'data': data
                }
            except:
                return {'success': False, 'error': 'Erro ao processar JSON'}
        else:
            return {'success': False, 'error': f'Status {response.status_code}'}

    except Exception as e:
        return {'success': False, 'error': f'Erro: {str(e)}'}


def fetch_transacoes_periodo(user_id, all_cookies, dias=30):
    """
    Busca transacoes detalhadas dos ultimos N dias.
    Endpoint: /api/front/users/{userId}/transactions
    """
    try:
        # Calcula datas
        from datetime import datetime, timedelta

        agora = datetime.utcnow()
        inicio = agora - timedelta(days=dias)

        # Formata datas no formato ISO 8601 (SEM encoding - requests faz isso automaticamente)
        until = agora.strftime('%Y-%m-%dT%H:%M:%SZ')
        from_date = inicio.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Endpoint descoberto
        url = f'https://br.platform.com/api/front/users/{user_id}/transactions'

        params = {
            'from': from_date,
            'until': until,
            'offset': 0,
            'limit': 200  # Maximo permitido pela API
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://br.platform.com/earnings/tokens-history',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }

        response = requests.get(url, headers=headers, cookies=all_cookies, params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()
            transacoes = data.get('transactions', [])

            return {
                'success': True,
                'transacoes': transacoes,
                'total': len(transacoes)
            }
        else:
            # Debug: captura resposta de erro
            try:
                error_body = response.text[:500]  # Primeiros 500 chars
            except:
                error_body = "Não foi possível ler corpo da resposta"

            return {
                'success': False,
                'error': f'Status {response.status_code}',
                'details': error_body,
                'url': response.url
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'Erro: {str(e)}'
        }


def agrupar_por_sessoes(transacoes, gap_horas=1):
    """
    Agrupa transacoes em sessoes baseado em gaps de tempo.
    Se passar mais de {gap_horas} hora(s) entre transacoes = sessao nova.
    """
    from datetime import datetime, timedelta

    if not transacoes:
        return []

    # Ordena por data (mais antiga primeiro)
    transacoes_sorted = sorted(transacoes, key=lambda x: x['date'])

    sessoes = []
    sessao_atual = {
        'inicio': None,
        'fim': None,
        'transacoes': [],
        'tokens_total': 0,
        'duracao_segundos': 0
    }

    gap_limite = timedelta(hours=gap_horas)

    for i, trans in enumerate(transacoes_sorted):
        data_trans = datetime.fromisoformat(trans['date'].replace('Z', '+00:00'))

        if i == 0:
            # Primeira transacao = inicio da primeira sessao
            sessao_atual['inicio'] = data_trans
            sessao_atual['fim'] = data_trans
            sessao_atual['transacoes'].append(trans)
            sessao_atual['tokens_total'] += trans['tokens']
        else:
            # Verifica gap com transacao anterior
            ultima_data = datetime.fromisoformat(transacoes_sorted[i-1]['date'].replace('Z', '+00:00'))
            gap = data_trans - ultima_data

            if gap > gap_limite:
                # Gap maior que limite = nova sessao
                # Finaliza sessao atual
                sessao_atual['duracao_segundos'] = (sessao_atual['fim'] - sessao_atual['inicio']).total_seconds()
                sessoes.append(sessao_atual.copy())

                # Inicia nova sessao
                sessao_atual = {
                    'inicio': data_trans,
                    'fim': data_trans,
                    'transacoes': [trans],
                    'tokens_total': trans['tokens'],
                    'duracao_segundos': 0
                }
            else:
                # Mesma sessao
                sessao_atual['fim'] = data_trans
                sessao_atual['transacoes'].append(trans)
                sessao_atual['tokens_total'] += trans['tokens']

    # Adiciona ultima sessao
    if sessao_atual['transacoes']:
        sessao_atual['duracao_segundos'] = (sessao_atual['fim'] - sessao_atual['inicio']).total_seconds()
        sessoes.append(sessao_atual)

    return sessoes


def calcular_duracao_sessao_inteligente(sessao):
    """
    Calcula duracao real estimada da sessao.
    Se duracao entre primeira e ultima transacao < 5min, assume pelo menos 30min de live.
    """
    duracao_transacoes = sessao['duracao_segundos']

    # Se duracao muito curta (varias gorjetas rapidas), assume tempo minimo
    if duracao_transacoes < 300:  # Menos de 5 minutos
        return max(1800, duracao_transacoes)  # Minimo 30min
    else:
        # Adiciona 15min no final (geralmente continua transmitindo apos ultima gorjeta)
        return duracao_transacoes + 900




def processar_csv_estoque(uploaded_file):
    """
    Processa CSV de estoque com regras especificas:
    - skiprows=3 (3 linhas de metadata)
    - Limpa colunas de currency brasileira
    """
    try:
        # Le CSV pulando 3 primeiras linhas de metadata
        df = pd.read_csv(uploaded_file, skiprows=3)

        # Identifica colunas de moeda para limpar
        colunas_moeda = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # Verifica se contem "R$" em alguma celula
                amostra = df[col].astype(str).head(5)
                if any('R$' in str(val) for val in amostra):
                    colunas_moeda.append(col)

        # Limpa colunas de moeda
        for col in colunas_moeda:
            df[f'{col}_limpo'] = df[col].apply(limpar_currency_br)

        return {
            'success': True,
            'df': df,
            'colunas_moeda': colunas_moeda
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao processar CSV: {str(e)}'
        }


def carregar_despesas():
    """Carrega dados de despesas do CSV."""
    if os.path.exists(DESPESAS_FILE):
        df = pd.read_csv(DESPESAS_FILE)
        df['data'] = pd.to_datetime(df['data']).dt.date
        return df
    return pd.DataFrame(columns=['data', 'item', 'valor', 'pagador'])


def salvar_despesas(df):
    """Salva dados de despesas no CSV."""
    df.to_csv(DESPESAS_FILE, index=False)


def salvar_cookies(cookies_dict):
    """Salva cookies em arquivo JSON local"""
    COOKIES_FILE = 'cookies_saved.json'
    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cookies_dict, f, indent=2)


def carregar_cookies_salvos():
    """Carrega cookies salvos do arquivo"""
    COOKIES_FILE = 'cookies_saved.json'
    if os.path.exists(COOKIES_FILE):
        try:
            with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None


# ==================== PRODUTOS & VENDAS ====================

def carregar_produtos():
    """Carrega produtos do arquivo JSON"""
    if os.path.exists(PRODUTOS_FILE):
        try:
            with open(PRODUTOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def salvar_produtos(produtos):
    """Salva produtos no arquivo JSON"""
    with open(PRODUTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(produtos, f, indent=2, ensure_ascii=False)


def carregar_vendas():
    """Carrega vendas do arquivo JSON"""
    if os.path.exists(VENDAS_FILE):
        try:
            with open(VENDAS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def salvar_vendas(vendas):
    """Salva vendas no arquivo JSON"""
    with open(VENDAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(vendas, f, indent=2, ensure_ascii=False)


def adicionar_produto(nome, quantidade_gramas, preco_compra, preco_venda, descricao=""):
    """Adiciona novo produto ao estoque"""
    produtos = carregar_produtos()
    novo_produto = {
        'id': len(produtos) + 1 if produtos else 1,
        'nome': nome,
        'descricao': descricao,
        'quantidade_gramas': quantidade_gramas,
        'quantidade_inicial': quantidade_gramas,
        'preco_compra_total': preco_compra,
        'preco_venda_grama': preco_venda,
        'vendido_gramas': 0,
        'data_cadastro': datetime.now().isoformat()
    }
    produtos.append(novo_produto)
    salvar_produtos(produtos)
    return novo_produto


def registrar_venda(produto_id, gramas_vendidas, valor_venda, observacao=""):
    """Registra uma venda parcial e atualiza estoque"""
    produtos = carregar_produtos()
    vendas = carregar_vendas()

    # Encontra produto
    produto = next((p for p in produtos if p['id'] == produto_id), None)
    if not produto:
        return False, "Produto não encontrado"

    # Verifica estoque
    if produto['quantidade_gramas'] < gramas_vendidas:
        return False, f"Estoque insuficiente. Disponível: {produto['quantidade_gramas']}g"

    # Atualiza estoque
    produto['quantidade_gramas'] -= gramas_vendidas
    produto['vendido_gramas'] += gramas_vendidas

    # Registra venda
    nova_venda = {
        'id': len(vendas) + 1 if vendas else 1,
        'produto_id': produto_id,
        'produto_nome': produto['nome'],
        'gramas': gramas_vendidas,
        'valor': valor_venda,
        'observacao': observacao,
        'data': datetime.now().isoformat()
    }
    vendas.append(nova_venda)

    salvar_produtos(produtos)
    salvar_vendas(vendas)

    return True, "Venda registrada com sucesso!"


def remover_produto(produto_id):
    """Remove produto do estoque"""
    produtos = carregar_produtos()
    produtos = [p for p in produtos if p['id'] != produto_id]
    salvar_produtos(produtos)
    return True


# ==================== INICIALIZACAO SESSION STATE ====================
if 'despesas_df' not in st.session_state:
    st.session_state.despesas_df = carregar_despesas()

if 'stipchat_data' not in st.session_state:
    st.session_state.stipchat_data = None

if 'estoque_df' not in st.session_state:
    st.session_state.estoque_df = None

if 'debug_endpoints_results' not in st.session_state:
    st.session_state.debug_endpoints_results = None

if 'debug_api_data' not in st.session_state:
    st.session_state.debug_api_data = None

if 'sessoes_data' not in st.session_state:
    st.session_state.sessoes_data = None

if 'transacoes_raw' not in st.session_state:
    st.session_state.transacoes_raw = None

if 'cookies_salvos' not in st.session_state:
    st.session_state.cookies_salvos = carregar_cookies_salvos()

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>💎 EMPIRE CONTROL 💎</h1>
    <p style="color: #888; margin: 5px 0 0 0; font-size: 1.1rem;">Financial Command Center</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR - FINANCIAL CONFIG ====================
st.sidebar.markdown("## 💰 Calibracao Financeira")

# Funcao para buscar cotacao USD/BRL da Binance
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_usdbrl_binance():
    """Busca cotacao USD/BRL da Binance API"""
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=USDTBRL', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data['price'])
        else:
            return 6.00  # Fallback
    except:
        return 6.00  # Fallback em caso de erro

# Busca cotacao automatica
cotacao_auto = get_usdbrl_binance()

st.sidebar.markdown(f"### 💵 Dólar Hoje: **R$ {cotacao_auto:.2f}**")
st.sidebar.caption("Cotação USDT/BRL via Binance (atualiza a cada 5 min)")

cotacao_dolar = cotacao_auto

st.sidebar.markdown("---")

st.sidebar.markdown(f"**🪙 1 Token = R$ {0.05 * cotacao_dolar:.2f}**")
st.sidebar.markdown(f"**🎯 Meta Diária = $100 USD**")

# ==================== TABS ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔴 REVENUE API",
    "📦 INVENTORY (STOCK)",
    "🏠 HOUSEHOLD EXPENSES",
    "📊 EXECUTIVE DASHBOARD"
])

# ==================== TAB 1: REVENUE API ====================
with tab1:
    st.markdown("### 🔴 Revenue Revenue Tracking")
    st.markdown("Rastreamento em tempo real via API escondida da plataforma")

    col_sync, col_result = st.columns([1, 2])

    with col_sync:
        st.markdown("#### 🔄 Sincronizar Dados")

        # Verifica se ja tem cookies salvos
        if st.session_state.cookies_salvos:
            st.success("✅ Cookies salvos encontrados")

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                atualizar_cookies = st.checkbox("Atualizar cookies", value=False)

            with col_btn2:
                if st.button("🗑️ Limpar cookies", use_container_width=True):
                    os.remove('cookies_saved.json')
                    st.session_state.cookies_salvos = None
                    st.rerun()
        else:
            atualizar_cookies = True
            st.info("📁 Faça upload dos cookies pela primeira vez")

        # Upload de cookies (só mostra se não tiver salvos ou se quiser atualizar)
        uploaded_cookies = None
        if atualizar_cookies:
            uploaded_cookies = st.file_uploader(
                "📁 Upload cookies.json",
                type=['json'],
                help="Arquivo JSON exportado da extensao de cookies"
            )

        # Periodo de historico
        dias_historico = st.selectbox(
            "📅 Período",
            options=[7, 15, 30, 60, 90],
            index=2,
            format_func=lambda x: f"{x} dias",
            help="Quantos dias de histórico buscar"
        )

        if st.button("🚀 SINCRONIZAR", type="primary", use_container_width=True):
            # Decide de onde pegar os cookies
            cookies_dict = None

            if uploaded_cookies:
                # Upload novo - processa e salva
                try:
                    cookies_raw = uploaded_cookies.read().decode('utf-8')
                    cookies_list = json.loads(cookies_raw)

                    # Converte lista de cookies para dict
                    cookies_dict = {}
                    for cookie in cookies_list:
                        if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                            cookies_dict[cookie['name']] = cookie['value']

                    if cookies_dict:
                        # Salva os cookies novos
                        salvar_cookies(cookies_dict)
                        st.session_state.cookies_salvos = cookies_dict
                except json.JSONDecodeError:
                    st.error("JSON invalido! Verifique o arquivo.")
                except Exception as e:
                    st.error(f"Erro: {str(e)}")
            elif st.session_state.cookies_salvos:
                # Usa cookies salvos
                cookies_dict = st.session_state.cookies_salvos
            else:
                st.error("Faca upload do arquivo cookies.json primeiro!")

            if cookies_dict:
                with st.spinner("Sincronizando dados..."):
                    # 1. Busca dados basicos (tokens totais, user info)
                    result = fetch_stipchat_stats_requests(None, all_cookies=cookies_dict)

                    if result['success']:
                        user_id = result['data']['initial']['client']['user']['id']

                        # 2. Busca historico de transacoes
                        with st.spinner(f"Carregando histórico de {dias_historico} dias..."):
                            transacoes_result = fetch_transacoes_periodo(user_id, cookies_dict, dias=dias_historico)

                        if transacoes_result['success']:
                            # 3. Agrupa em sessoes
                            sessoes = agrupar_por_sessoes(transacoes_result['transacoes'], gap_horas=1)

                            # Guarda dados
                            st.session_state.stipchat_data = result
                            st.session_state.transacoes_raw = transacoes_result['transacoes']
                            st.session_state.sessoes_data = sessoes

                            st.success(f"✅ Sincronizado! {result['tokens']} tokens | {len(sessoes)} sessões")
                            st.rerun()
                        else:
                            st.error(f"Erro ao buscar transações: {transacoes_result['error']}")
                    else:
                        st.error(f"Erro: {result['error']}")
                        st.warning("Cookies expirados? Atualize fazendo novo upload.")

    with col_result:
        st.markdown("#### 📊 Analytics Dashboard")

        if st.session_state.sessoes_data:
            from datetime import datetime
            import pandas as pd

            sessoes = st.session_state.sessoes_data
            data = st.session_state.stipchat_data

            tokens_total = data['tokens']
            transacoes = st.session_state.transacoes_raw

            # Calcula metricas avancadas
            revenue_total = tokens_total * 0.05 * cotacao_dolar
            total_transacoes = len(transacoes)
            clientes_unicos = len(set(t['username'] for t in transacoes if t.get('username')))

            # Horas totais trabalhadas
            horas_totais = sum(calcular_duracao_sessao_inteligente(s) for s in sessoes) / 3600
            taxa_hora_geral = revenue_total / horas_totais if horas_totais > 0 else 0

            # Ticket medio
            ticket_medio = tokens_total / total_transacoes if total_transacoes > 0 else 0

            # KPIs Principais - Linha 1
            col_k1, col_k2, col_k3, col_k4 = st.columns(4)

            with col_k1:
                st.markdown(f"""
                <div class="kpi-card">
                    <p class="kpi-title">💰 Revenue Total</p>
                    <p class="kpi-value-green">R$ {revenue_total:,.2f}</p>
                    <p style="font-size: 0.75rem; color: #666; margin-top: 8px;">{tokens_total:,} tokens</p>
                </div>
                """, unsafe_allow_html=True)

            with col_k2:
                st.markdown(f"""
                <div class="kpi-card">
                    <p class="kpi-title">📈 R$/Hora Média</p>
                    <p class="kpi-value-blue">R$ {taxa_hora_geral:,.2f}/h</p>
                    <p style="font-size: 0.75rem; color: #666; margin-top: 8px;">{horas_totais:.1f}h trabalhadas</p>
                </div>
                """, unsafe_allow_html=True)

            with col_k3:
                st.markdown(f"""
                <div class="kpi-card">
                    <p class="kpi-title">👥 Clientes Únicos</p>
                    <p class="kpi-value-purple">{clientes_unicos:,}</p>
                    <p style="font-size: 0.75rem; color: #666; margin-top: 8px;">{total_transacoes} transações</p>
                </div>
                """, unsafe_allow_html=True)

            with col_k4:
                st.markdown(f"""
                <div class="kpi-card">
                    <p class="kpi-title">🎯 Ticket Médio</p>
                    <p class="kpi-value-gold">{ticket_medio:.1f} tokens</p>
                    <p style="font-size: 0.75rem; color: #666; margin-top: 8px;">R$ {ticket_medio * 0.05 * cotacao_dolar:.2f} média</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Analytics Mensal
            st.markdown("#### 📅 Performance Mensal")

            from collections import defaultdict
            import calendar as cal

            faturamento_por_mes = defaultdict(lambda: {'tokens': 0, 'usd': 0.0, 'dias': set(), 'sessoes': 0})

            for sessao in sessoes:
                data_sessao = sessao['inicio'].astimezone().date()
                mes_ano = data_sessao.strftime('%Y-%m')  # ex: 2025-12
                tokens = sessao['tokens_total']
                usd = tokens * 0.05

                faturamento_por_mes[mes_ano]['tokens'] += tokens
                faturamento_por_mes[mes_ano]['usd'] += usd
                faturamento_por_mes[mes_ano]['dias'].add(data_sessao)
                faturamento_por_mes[mes_ano]['sessoes'] += 1

            # Ordena por mes (mais recente primeiro)
            meses_ordenados = sorted(faturamento_por_mes.items(), key=lambda x: x[0], reverse=True)

            if meses_ordenados:
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)

                for idx, (mes_ano, info) in enumerate(meses_ordenados[:4]):  # Mostra últimos 4 meses
                    ano, mes_num = mes_ano.split('-')
                    nome_mes = cal.month_name[int(mes_num)]
                    dias_trabalhados = len(info['dias'])
                    meta_mes = dias_trabalhados * 100  # $100 por dia de live
                    percentual_meta = (info['usd'] / meta_mes * 100) if meta_mes > 0 else 0
                    cor_meta = "green" if percentual_meta >= 100 else "blue" if percentual_meta >= 75 else "red"

                    col = [col_m1, col_m2, col_m3, col_m4][idx]
                    with col:
                        st.markdown(f"""
                        <div class="kpi-card">
                            <p class="kpi-title">💵 {nome_mes}/{ano}</p>
                            <p class="kpi-value-{cor_meta}">${info['usd']:.2f} USD</p>
                            <p style="font-size: 0.75rem; color: #666; margin-top: 8px;">
                                {dias_trabalhados} dias | {info['sessoes']} sessões<br>
                                Meta: ${meta_mes:.0f} ({percentual_meta:.0f}%)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("---")

            # Seletor de Visualizacao
            st.markdown("#### 🎯 Visualização")

            col_filtro1, col_filtro2 = st.columns([2, 1])

            with col_filtro1:
                filtro = st.radio(
                    "Modo:",
                    options=["Hoje", "Últimas 24h", "Última Semana", "Mês Atual", "Calendário", "Todas"],
                    horizontal=True,
                    index=0
                )

            with col_filtro2:
                if filtro == "Calendário":
                    data_selecionada = st.date_input(
                        "Selecione o dia:",
                        value=date.today(),
                        max_value=date.today()
                    )

            # Aplica filtros
            from datetime import datetime, timedelta, timezone
            import calendar as cal

            agora_utc = datetime.now(timezone.utc)
            sessoes_filtradas = sessoes.copy()

            if filtro == "Hoje":
                # Desde 00h de hoje (timezone local)
                hoje_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                hoje_inicio_utc = hoje_inicio.astimezone(timezone.utc)
                sessoes_filtradas = [s for s in sessoes if s['fim'] >= hoje_inicio_utc]
            elif filtro == "Últimas 24h":
                inicio_24h = agora_utc - timedelta(hours=24)
                sessoes_filtradas = [s for s in sessoes if s['fim'] >= inicio_24h]
            elif filtro == "Última Semana":
                inicio_semana = agora_utc - timedelta(days=7)
                sessoes_filtradas = [s for s in sessoes if s['fim'] >= inicio_semana]
            elif filtro == "Mês Atual":
                hoje = datetime.now().date()
                inicio_mes = hoje.replace(day=1)
                inicio_mes_dt = datetime.combine(inicio_mes, datetime.min.time()).astimezone(timezone.utc)
                sessoes_filtradas = [s for s in sessoes if s['fim'] >= inicio_mes_dt]
            elif filtro == "Calendário":
                # Filtra pelo dia selecionado
                inicio_dia = datetime.combine(data_selecionada, datetime.min.time()).astimezone(timezone.utc)
                fim_dia = datetime.combine(data_selecionada, datetime.max.time()).astimezone(timezone.utc)
                sessoes_filtradas = [s for s in sessoes if inicio_dia <= s['fim'] <= fim_dia]

            # Filtra transacoes pelo mesmo periodo
            transacoes_filtradas = []
            for sessao in sessoes_filtradas:
                transacoes_filtradas.extend(sessao['transacoes'])

            # Top Clientes Analytics
            st.markdown("---")

            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.markdown("#### 👑 Top 10 Clientes (Maiores Gastadores)")

                # Agrupa por cliente
                from collections import defaultdict
                gastos_por_cliente = defaultdict(lambda: {'tokens': 0, 'transacoes': 0, 'revenue': 0.0})

                for trans in transacoes_filtradas:
                    username = trans.get('username', 'Anônimo')
                    tokens = trans.get('tokens', 0)
                    gastos_por_cliente[username]['tokens'] += tokens
                    gastos_por_cliente[username]['transacoes'] += 1
                    gastos_por_cliente[username]['revenue'] += tokens * 0.05 * cotacao_dolar

                # Ordena por tokens (decrescente)
                top_clientes = sorted(gastos_por_cliente.items(), key=lambda x: x[1]['tokens'], reverse=True)[:10]

                if top_clientes:
                    # Cria DataFrame
                    top_df = pd.DataFrame([
                        {
                            'Cliente': username[:20] + '...' if len(username) > 20 else username,
                            'Tokens': f"{info['tokens']:,}",
                            'Tips': info['transacoes'],
                            'Revenue': f"R$ {info['revenue']:.2f}",
                            'Ticket': f"{info['tokens']/info['transacoes']:.1f}" if info['transacoes'] > 0 else '0'
                        }
                        for username, info in top_clientes
                    ])

                    st.dataframe(top_df, use_container_width=True, hide_index=True)

                    # Total representado pelos top 10
                    total_top10 = sum(info['tokens'] for _, info in top_clientes)
                    percentual_top10 = (total_top10 / tokens_total * 100) if tokens_total > 0 else 0
                    st.caption(f"Top 10 representa {percentual_top10:.1f}% do total ({total_top10:,} tokens)")
                else:
                    st.info("Nenhum cliente encontrado neste período")

            with col_chart2:
                st.markdown("#### 📊 Distribuição de Revenue")

                if top_clientes:
                    # Grafico de pizza
                    labels = [username[:15] + '...' if len(username) > 15 else username for username, _ in top_clientes]
                    values = [info['revenue'] for _, info in top_clientes]

                    fig = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.4,
                        marker=dict(colors=px.colors.sequential.Viridis),
                        textinfo='label+percent',
                        textposition='auto',
                    )])

                    fig.update_layout(
                        showlegend=False,
                        height=350,
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#ffffff', size=10)
                    )

                    st.plotly_chart(fig, use_container_width=True)

            # Graficos de Tendencia Temporal
            st.markdown("---")
            st.markdown("#### 📈 Análise Temporal")

            col_time1, col_time2 = st.columns(2)

            with col_time1:
                # Grafico: Tokens por Dia
                from collections import defaultdict
                tokens_por_dia = defaultdict(int)

                for sessao in sessoes_filtradas:
                    data_local = sessao['inicio'].astimezone().date()
                    tokens_por_dia[data_local] += sessao['tokens_total']

                if tokens_por_dia:
                    df_timeline = pd.DataFrame([
                        {'Data': data, 'Tokens': tokens}
                        for data, tokens in sorted(tokens_por_dia.items())
                    ])

                    fig_timeline = px.area(
                        df_timeline,
                        x='Data',
                        y='Tokens',
                        title='Tokens por Dia',
                        color_discrete_sequence=['#00ff88']
                    )

                    fig_timeline.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(26,26,26,1)',
                        font=dict(color='#ffffff'),
                        height=300,
                        margin=dict(l=40, r=20, t=40, b=40),
                        xaxis=dict(gridcolor='#333333'),
                        yaxis=dict(gridcolor='#333333')
                    )

                    st.plotly_chart(fig_timeline, use_container_width=True)

            with col_time2:
                # Grafico: R$/Hora por Sessão
                if sessoes_filtradas:
                    taxa_por_sessao = []
                    for i, sessao in enumerate(sessoes_filtradas):
                        horas = calcular_duracao_sessao_inteligente(sessao) / 3600
                        revenue_sessao = sessao['tokens_total'] * 0.05 * cotacao_dolar
                        taxa = revenue_sessao / horas if horas > 0 else 0
                        taxa_por_sessao.append({
                            'Sessão': f"S{i+1}",
                            'R$/hora': taxa
                        })

                    df_taxa = pd.DataFrame(taxa_por_sessao)

                    fig_taxa = px.bar(
                        df_taxa,
                        x='Sessão',
                        y='R$/hora',
                        title='Performance por Sessão (R$/hora)',
                        color='R$/hora',
                        color_continuous_scale='Viridis'
                    )

                    fig_taxa.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(26,26,26,1)',
                        font=dict(color='#ffffff'),
                        height=300,
                        margin=dict(l=40, r=20, t=40, b=40),
                        xaxis=dict(gridcolor='#333333'),
                        yaxis=dict(gridcolor='#333333'),
                        showlegend=False
                    )

                    st.plotly_chart(fig_taxa, use_container_width=True)

            # Insights Automaticos
            st.markdown("---")
            st.markdown("#### 💡 Insights & Recomendações")

            col_insight1, col_insight2, col_insight3, col_insight4 = st.columns(4)

            with col_insight1:
                # Melhor sessao
                if sessoes_filtradas:
                    melhor_sessao = max(sessoes_filtradas, key=lambda s: s['tokens_total'])
                    melhor_revenue = melhor_sessao['tokens_total'] * 0.05 * cotacao_dolar
                    melhor_data = melhor_sessao['inicio'].astimezone().strftime('%d/%m %H:%M')

                    st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-title">🏆 Melhor Sessão</p>
                        <p class="kpi-value-green">{melhor_sessao['tokens_total']:,} tokens</p>
                        <p style="font-size: 0.75rem; color: #666; margin-top: 8px;">{melhor_data} | R$ {melhor_revenue:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

            with col_insight2:
                # Cliente mais generoso
                if gastos_por_cliente:
                    top1_cliente, top1_info = top_clientes[0]
                    st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-title">👑 Top Cliente</p>
                        <p class="kpi-value-purple">{top1_info['tokens']:,} tokens</p>
                        <p style="font-size: 0.75rem; color: #666; margin-top: 8px;">{top1_cliente[:20]}</p>
                    </div>
                    """, unsafe_allow_html=True)

            with col_insight3:
                # Meta diaria $100 USD
                if sessoes_filtradas:
                    tokens_filtradas_total = sum(s['tokens_total'] for s in sessoes_filtradas)
                    usd_total = tokens_filtradas_total * 0.05
                    dias_unicos = len(set(s['inicio'].astimezone().date() for s in sessoes_filtradas))
                    meta_total = dias_unicos * 100
                    percentual_meta = (usd_total / meta_total * 100) if meta_total > 0 else 0
                    cor_meta = "green" if percentual_meta >= 100 else "blue" if percentual_meta >= 75 else "red"

                    st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-title">🎯 Meta $100/dia</p>
                        <p class="kpi-value-{cor_meta}">{percentual_meta:.0f}%</p>
                        <p style="font-size: 0.75rem; color: #666; margin-top: 8px;">${usd_total:.2f} / ${meta_total:.0f}</p>
                    </div>
                    """, unsafe_allow_html=True)

            with col_insight4:
                # Crescimento (compara ultima vs penultima sessao)
                if len(sessoes_filtradas) >= 2:
                    ultima = sessoes_filtradas[-1]['tokens_total']
                    penultima = sessoes_filtradas[-2]['tokens_total']
                    crescimento = ((ultima - penultima) / penultima * 100) if penultima > 0 else 0
                    cor = "green" if crescimento >= 0 else "red"
                    simbolo = "↑" if crescimento >= 0 else "↓"

                    st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-title">📊 Tendência</p>
                        <p class="kpi-value-{cor}">{simbolo} {abs(crescimento):.1f}%</p>
                        <p style="font-size: 0.75rem; color: #666; margin-top: 8px;">última vs penúltima</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Mostra sessoes filtradas
            st.markdown("---")
            st.markdown("#### 🎥 Detalhamento de Sessões")

            if sessoes_filtradas:
                tokens_filtradas = sum(s['tokens_total'] for s in sessoes_filtradas)
                revenue_filtradas = tokens_filtradas * 0.05 * cotacao_dolar

                st.markdown(f"**{len(sessoes_filtradas)} sessão(ões) | {tokens_filtradas:,} tokens | R$ {revenue_filtradas:,.2f}**")

                st.markdown("---")

                # Lista de sessoes
                for i, sessao in enumerate(reversed(sessoes_filtradas)):
                    # Converte para timezone local para exibicao
                    inicio_local = sessao['inicio'].astimezone()
                    fim_local = sessao['fim'].astimezone()

                    duracao_real = calcular_duracao_sessao_inteligente(sessao)
                    horas = duracao_real / 3600
                    revenue = sessao['tokens_total'] * 0.05 * cotacao_dolar
                    taxa_hora = revenue / horas if horas > 0 else 0

                    data_str = inicio_local.strftime('%d/%m/%Y')
                    hora_inicio = inicio_local.strftime('%H:%M')
                    hora_fim = fim_local.strftime('%H:%M')

                    with st.expander(f"🎥 Sessão {len(sessoes_filtradas)-i} - {data_str} ({hora_inicio}-{hora_fim})", expanded=(i==0)):
                        col_s1, col_s2, col_s3 = st.columns(3)

                        with col_s1:
                            st.metric("🪙 Tokens", f"{sessao['tokens_total']:,}")
                        with col_s2:
                            st.metric("⏱️ Duração", f"{horas:.1f}h")
                        with col_s3:
                            st.metric("💰 Revenue", f"R$ {revenue:,.2f}")

                        st.metric("📈 R$/hora", f"R$ {taxa_hora:,.2f}/h")
                        st.caption(f"{len(sessao['transacoes'])} transações | {hora_inicio} - {hora_fim}")
            else:
                st.info(f"Nenhuma sessão encontrada para o filtro '{filtro}'")

            # Breakdown Diário
            st.markdown("---")
            st.markdown("#### 📅 Breakdown Diário")

            # Agrupa sessões por dia
            from collections import defaultdict

            breakdown_por_dia = defaultdict(lambda: {'tokens': 0, 'horas': 0.0, 'sessoes': 0, 'revenue': 0.0})

            for sessao in sessoes_filtradas:
                # Usa data de inicio da sessao (timezone local)
                data_local = sessao['inicio'].astimezone().date()
                duracao_horas = calcular_duracao_sessao_inteligente(sessao) / 3600
                revenue = sessao['tokens_total'] * 0.05 * cotacao_dolar

                breakdown_por_dia[data_local]['tokens'] += sessao['tokens_total']
                breakdown_por_dia[data_local]['horas'] += duracao_horas
                breakdown_por_dia[data_local]['sessoes'] += 1
                breakdown_por_dia[data_local]['revenue'] += revenue

            # Ordena por data (mais recente primeiro)
            breakdown_ordenado = sorted(breakdown_por_dia.items(), key=lambda x: x[0], reverse=True)

            if breakdown_ordenado:
                # Cria DataFrame para exibicao
                breakdown_df = pd.DataFrame([
                    {
                        'Data': data.strftime('%d/%m/%Y'),
                        'Sessões': info['sessoes'],
                        'Tokens': f"{info['tokens']:,}",
                        'Horas': f"{info['horas']:.1f}h",
                        'Revenue': f"R$ {info['revenue']:.2f}",
                        'R$/hora': f"R$ {info['revenue']/info['horas']:.2f}/h" if info['horas'] > 0 else "R$ 0/h"
                    }
                    for data, info in breakdown_ordenado
                ])

                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

                # Totais
                total_dias = len(breakdown_ordenado)
                total_tokens_breakdown = sum(info['tokens'] for _, info in breakdown_ordenado)
                total_horas_breakdown = sum(info['horas'] for _, info in breakdown_ordenado)
                total_revenue_breakdown = sum(info['revenue'] for _, info in breakdown_ordenado)
                media_hora = total_revenue_breakdown / total_horas_breakdown if total_horas_breakdown > 0 else 0

                col_t1, col_t2, col_t3, col_t4 = st.columns(4)
                with col_t1:
                    st.metric("📆 Total Dias", total_dias)
                with col_t2:
                    st.metric("🪙 Total Tokens", f"{total_tokens_breakdown:,}")
                with col_t3:
                    st.metric("⏱️ Total Horas", f"{total_horas_breakdown:.1f}h")
                with col_t4:
                    st.metric("💰 Média/hora", f"R$ {media_hora:.2f}/h")
            else:
                st.info("Nenhum dado disponível para breakdown diário")

        else:
            st.info("Sincronize com cookies para ver análise de sessões")

# ==================== TAB 2: GESTAO DE PRODUTOS ====================
with tab2:
    st.markdown("### 📦 Gestão de Produtos & Estoque")
    st.markdown("Controle completo de produtos, vendas e lucro")

    # Carrega dados
    produtos = carregar_produtos()
    vendas = carregar_vendas()

    # Layout em 3 colunas
    col_add, col_sell, col_dashboard = st.columns([1, 1, 2])

    # COLUNA 1: Adicionar Produto
    with col_add:
        st.markdown("#### ➕ Novo Produto")

        with st.form("form_produto", clear_on_submit=True):
            prod_nome = st.text_input("📝 Nome", placeholder="Ex: Creatina")
            prod_desc = st.text_area("💬 Descrição", placeholder="Ex: Creatina monohidratada pura", height=80)
            prod_gramas = st.number_input("⚖️ Quantidade (gramas)", min_value=0, value=100, step=10)
            prod_preco_compra = st.number_input("💰 Preço Compra Total (R$)", min_value=0.0, value=0.0, step=1.0)
            prod_preco_venda_g = st.number_input("💵 Preço Venda por Grama (R$)", min_value=0.0, value=0.0, step=0.01)

            btn_add_prod = st.form_submit_button("✅ Adicionar Produto", use_container_width=True, type="primary")

            if btn_add_prod and prod_nome and prod_gramas > 0:
                adicionar_produto(prod_nome, prod_gramas, prod_preco_compra, prod_preco_venda_g, prod_desc)
                st.success(f"{prod_nome} adicionado!")
                st.rerun()

    # COLUNA 2: Registrar Venda
    with col_sell:
        st.markdown("#### 💸 Registrar Venda")

        if produtos:
            with st.form("form_venda", clear_on_submit=True):
                # Seletor de produto
                produto_opcoes = {f"{p['nome']} ({p['quantidade_gramas']}g disponível)": p['id'] for p in produtos if p['quantidade_gramas'] > 0}

                if produto_opcoes:
                    produto_selecionado = st.selectbox("📦 Produto", list(produto_opcoes.keys()))
                    produto_id = produto_opcoes[produto_selecionado]

                    # Pega produto para mostrar info
                    produto = next(p for p in produtos if p['id'] == produto_id)

                    st.caption(f"Preço sugerido: R$ {produto['preco_venda_grama']:.2f}/g")

                    venda_gramas = st.number_input("⚖️ Gramas Vendidas", min_value=1, max_value=int(produto['quantidade_gramas']), value=10, step=5)
                    venda_valor = st.number_input("💰 Valor da Venda (R$)", min_value=0.0, value=float(venda_gramas * produto['preco_venda_grama']), step=1.0)
                    venda_obs = st.text_input("💬 Observação", placeholder="Ex: Cliente João, WhatsApp")

                    btn_vender = st.form_submit_button("✅ Confirmar Venda", use_container_width=True, type="primary")

                    if btn_vender:
                        sucesso, msg = registrar_venda(produto_id, venda_gramas, venda_valor, venda_obs)
                        if sucesso:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.warning("Nenhum produto com estoque disponível")
        else:
            st.info("Adicione produtos primeiro")

    # COLUNA 3: Dashboard de Produtos
    with col_dashboard:
        st.markdown("#### 📊 Dashboard de Produtos")

        if produtos:
            # KPIs Gerais
            investimento_total = sum(p['preco_compra_total'] for p in produtos)
            valor_vendido = sum(v['valor'] for v in vendas)
            lucro_bruto = valor_vendido - sum(
                (p['vendido_gramas'] / p['quantidade_inicial']) * p['preco_compra_total']
                for p in produtos if p['quantidade_inicial'] > 0
            )

            col_k1, col_k2, col_k3 = st.columns(3)

            with col_k1:
                st.markdown(f"""
                <div class="kpi-card">
                    <p class="kpi-title">💰 Investido</p>
                    <p class="kpi-value-blue">R$ {investimento_total:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            with col_k2:
                st.markdown(f"""
                <div class="kpi-card">
                    <p class="kpi-title">💵 Vendido</p>
                    <p class="kpi-value-green">R$ {valor_vendido:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            with col_k3:
                cor_lucro = "green" if lucro_bruto > 0 else "red"
                st.markdown(f"""
                <div class="kpi-card">
                    <p class="kpi-title">📈 Lucro</p>
                    <p class="kpi-value-{cor_lucro}">R$ {lucro_bruto:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Tabela de Produtos
            st.markdown("**📦 Estoque Atual**")

            produtos_df = pd.DataFrame([
                {
                    'Produto': p['nome'],
                    'Estoque': f"{p['quantidade_gramas']}g",
                    'Vendido': f"{p['vendido_gramas']}g",
                    '% Vendido': f"{(p['vendido_gramas']/p['quantidade_inicial']*100):.0f}%" if p['quantidade_inicial'] > 0 else "0%",
                    'R$/g': f"R$ {p['preco_venda_grama']:.2f}",
                    'ID': p['id']
                }
                for p in produtos
            ])

            st.dataframe(produtos_df.drop('ID', axis=1), use_container_width=True, hide_index=True)

            # Botões de ação
            col_del1, col_del2 = st.columns(2)

            with col_del1:
                produto_para_remover = st.selectbox("🗑️ Remover produto", [f"{p['nome']}" for p in produtos], key="del_prod")

            with col_del2:
                if st.button("🗑️ Confirmar Remoção", use_container_width=True):
                    produto_id = next(p['id'] for p in produtos if p['nome'] == produto_para_remover)
                    remover_produto(produto_id)
                    st.success(f"{produto_para_remover} removido!")
                    st.rerun()

        else:
            st.info("Nenhum produto cadastrado ainda")

# ==================== TAB 3: HOUSEHOLD EXPENSES ====================
with tab3:
    st.markdown("### 🏠 Household Expenses (Split 50/50)")

    col_form, col_hist = st.columns([1, 1.5])

    with col_form:
        st.markdown("#### ➕ Adicionar Despesa")

        with st.form("form_despesa", clear_on_submit=True):
            desp_data = st.date_input("📅 Data", value=date.today())
            desp_item = st.text_input("📝 Item/Descricao")
            desp_valor = st.number_input("💰 Valor (R$)", min_value=0.0, max_value=100000.0, value=0.0, step=5.0)
            desp_pagador = st.selectbox("👤 Pagador", options=["LO", "Companheira"])

            btn_add = st.form_submit_button("✅ Adicionar Gasto", use_container_width=True, type="primary")

            if btn_add and desp_valor > 0 and desp_item:
                nova_despesa = pd.DataFrame([{
                    'data': desp_data,
                    'item': desp_item,
                    'valor': round(desp_valor, 2),
                    'pagador': desp_pagador
                }])

                st.session_state.despesas_df = pd.concat([st.session_state.despesas_df, nova_despesa], ignore_index=True)
                salvar_despesas(st.session_state.despesas_df)
                st.success(f"Gasto de R$ {desp_valor:.2f} adicionado!")
                st.rerun()

    with col_hist:
        st.markdown("#### 📋 Historico de Despesas")

        if len(st.session_state.despesas_df) > 0:
            display_desp = st.session_state.despesas_df.copy()
            display_desp = display_desp.sort_values('data', ascending=False)

            st.dataframe(
                display_desp,
                use_container_width=True,
                column_config={
                    "data": st.column_config.DateColumn("📅 Data"),
                    "item": st.column_config.TextColumn("📝 Item"),
                    "valor": st.column_config.NumberColumn("💰 Valor", format="R$ %.2f"),
                    "pagador": st.column_config.TextColumn("👤 Pagador")
                },
                hide_index=True
            )

            total_despesas = display_desp['valor'].sum()
            st.markdown(f"**Total de Despesas: R$ {total_despesas:,.2f}**")

            if st.button("🗑️ Limpar Historico", type="secondary"):
                st.session_state.despesas_df = pd.DataFrame(columns=['data', 'item', 'valor', 'pagador'])
                salvar_despesas(st.session_state.despesas_df)
                st.rerun()
        else:
            st.info("Nenhuma despesa registrada")

# ==================== TAB 4: EXECUTIVE DASHBOARD ====================
with tab4:
    st.markdown("### 📊 Executive Dashboard - Visao Consolidada")

    # Calcular totais de cada fonte

    # 1. Revenue Revenue
    stipchat_revenue = 0
    if st.session_state.stipchat_data:
        tokens = st.session_state.stipchat_data['tokens']
        stipchat_revenue = tokens * 0.05 * cotacao_dolar

    # 2. Stock Profit
    stock_profit = 0
    if st.session_state.estoque_df is not None:
        # Tentar encontrar coluna LUCRO
        for col in st.session_state.estoque_df.columns:
            if 'LUCRO' in col.upper() and '_limpo' in col:
                stock_profit = st.session_state.estoque_df[col].sum()
                break

    # 3. Total Expenses
    total_expenses = 0
    if len(st.session_state.despesas_df) > 0:
        total_expenses = st.session_state.despesas_df['valor'].sum()

    # GRAND TOTAL LOGIC
    grand_total = stipchat_revenue + stock_profit - total_expenses

    # Display Grand Total
    st.markdown("#### 💎 GRAND TOTAL (Lucro Global)")

    if grand_total > 0:
        st.markdown(f"""
        <div class="success-box">
            <p style="color: #888; margin: 0; font-size: 0.9rem; text-transform: uppercase;">LUCRO GLOBAL (POSITIVO)</p>
            <p class="neon-green" style="margin: 10px 0;">R$ {grand_total:,.2f}</p>
            <p style="color: #00ff88; font-size: 1rem; margin: 0;">O imperio esta crescendo!</p>
        </div>
        """, unsafe_allow_html=True)
    elif grand_total < 0:
        st.markdown(f"""
        <div class="warning-box">
            <p style="color: #888; margin: 0; font-size: 0.9rem; text-transform: uppercase;">PREJUIZO GLOBAL (NEGATIVO)</p>
            <p class="neon-red" style="margin: 10px 0;">R$ {grand_total:,.2f}</p>
            <p style="color: #ff4444; font-size: 1rem; margin: 0;">Atencao: gastos superaram receitas</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-box">
            <p style="color: #888; margin: 0; font-size: 0.9rem; text-transform: uppercase;">LUCRO GLOBAL (EQUILIBRIO)</p>
            <p style="color: #fff; font-size: 2rem; font-weight: bold; margin: 10px 0;">R$ 0,00</p>
            <p style="color: #888; font-size: 1rem; margin: 0;">Receitas e gastos empatados</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Breakdown por fonte
    st.markdown("#### 📊 Breakdown por Fonte")

    col_b1, col_b2, col_b3 = st.columns(3)

    with col_b1:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-title">🔴 REVENUE REVENUE</p>
            <p class="kpi-value-green">R$ {stipchat_revenue:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_b2:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-title">📦 STOCK PROFIT</p>
            <p class="kpi-value-green">R$ {stock_profit:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_b3:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-title">💸 TOTAL EXPENSES</p>
            <p class="kpi-value-red">R$ {total_expenses:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Acerto de contas (Split 50/50)
    st.markdown("#### 💸 Acerto de Contas (Split 50/50)")

    if len(st.session_state.despesas_df) > 0:
        total_lo = st.session_state.despesas_df[st.session_state.despesas_df['pagador'] == 'LO']['valor'].sum()
        total_companheira = st.session_state.despesas_df[st.session_state.despesas_df['pagador'] == 'Companheira']['valor'].sum()
        total_geral = total_lo + total_companheira

        cada_um_deve = total_geral / 2

        saldo_lo = total_lo - cada_um_deve
        saldo_companheira = total_companheira - cada_um_deve

        col_s1, col_s2, col_s3 = st.columns(3)

        with col_s1:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-title">👩‍💼 LO Pagou</p>
                <p class="kpi-value-gold">R$ {total_lo:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_s2:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-title">👩 Companheira Pagou</p>
                <p class="kpi-value-gold">R$ {total_companheira:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_s3:
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-title">📊 Total Geral</p>
                <p style="color: #fff; font-size: 2rem; font-weight: bold;">R$ {total_geral:,.2f}</p>
                <p style="color: #888; font-size: 0.9rem;">Cada um: R$ {cada_um_deve:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)

        # Quem deve para quem
        if abs(saldo_lo) > 0.01:
            if saldo_lo > 0:
                st.markdown(f"""
                <div class="settlement-box">
                    <p style="color: #ffd700; font-size: 0.9rem; margin: 0; text-transform: uppercase;">⚠️ ACERTO PENDENTE</p>
                    <h2 style="color: #fff; margin: 15px 0; font-size: 1.3rem;">Companheira deve para LO</h2>
                    <p class="neon-green" style="margin: 0;">R$ {abs(saldo_lo):,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="settlement-box">
                    <p style="color: #ffd700; font-size: 0.9rem; margin: 0; text-transform: uppercase;">⚠️ ACERTO PENDENTE</p>
                    <h2 style="color: #fff; margin: 15px 0; font-size: 1.3rem;">LO deve para Companheira</h2>
                    <p class="neon-green" style="margin: 0;">R$ {abs(saldo_lo):,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-box">
                <h2 style="color: #00ff88; margin: 0; font-size: 1.4rem;">Tudo Acertado!</h2>
                <p style="color: #888; margin: 10px 0 0 0;">As contas estao equilibradas</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Registre despesas para ver o acerto de contas")

    st.markdown("---")

    # Grafico de composicao de receita
    st.markdown("#### 📊 Composicao da Receita")

    if stipchat_revenue > 0 or stock_profit > 0:
        receita_data = pd.DataFrame({
            'Fonte': ['Revenue', 'Stock'],
            'Valor': [stipchat_revenue, stock_profit]
        })

        fig = px.pie(
            receita_data,
            values='Valor',
            names='Fonte',
            color_discrete_sequence=['#00ff88', '#ffd700'],
            hole=0.4
        )

        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma receita registrada ainda")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>💎 Empire Control | Built for LO | Streamlit + Python 3.10+</p>
</div>
""", unsafe_allow_html=True)
