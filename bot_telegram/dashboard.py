#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Web - Sistema de Gerenciamento de Vendas de Conteúdo
Desenvolvido para GirlfrienDine Bot
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from functools import wraps
import json
import os
from datetime import datetime, timedelta
from catalog_system import (
    load_catalog, load_purchases, 
    get_all_active_contents, get_user_purchases,
    CATEGORIES
)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

ADMIN_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "DinaGostosa2025!")  # Trocar em produção

# =============================================================================
# AUTENTICAÇÃO
# =============================================================================

def login_required(f):
    """Decorador para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# ROTAS DE AUTENTICAÇÃO
# =============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Senha incorreta!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# =============================================================================
# DASHBOARD - ROTAS PRINCIPAIS
# =============================================================================

@app.route('/')
@login_required
def index():
    """Dashboard principal"""
    catalog = load_catalog()
    purchases = load_purchases()
    
    # Estatísticas gerais
    total_contents = len([c for c in catalog.values() if c.get('active', True)])
    total_sales = len([p for p in purchases.values() if p.get('status') == 'completed'])
    total_revenue = sum([p.get('amount', 0) for p in purchases.values() if p.get('status') == 'completed'])
    pending_deliveries = len([p for p in purchases.values() if p.get('status') == 'completed' and not p.get('delivered', False)])
    
    # Vendas recentes (últimas 10)
    recent_sales = sorted(
        [{"id": pid, **pdata} for pid, pdata in purchases.items() if pdata.get('status') == 'completed'],
        key=lambda x: x.get('purchased_at', ''),
        reverse=True
    )[:10]
    
    # Top conteúdos mais vendidos
    content_sales = {}
    for purchase in purchases.values():
        if purchase.get('status') == 'completed':
            content_id = purchase.get('content_id')
            content_sales[content_id] = content_sales.get(content_id, 0) + 1
    
    top_contents = sorted(
        [{"content_id": cid, "sales": count} for cid, count in content_sales.items()],
        key=lambda x: x['sales'],
        reverse=True
    )[:5]
    
    # Adicionar informações dos conteúdos
    for item in top_contents:
        content = catalog.get(item['content_id'], {})
        item['title'] = content.get('title', 'N/A')
        item['price'] = content.get('price', 0)
        item['revenue'] = item['sales'] * item['price']
    
    return render_template(
        'index.html',
        total_contents=total_contents,
        total_sales=total_sales,
        total_revenue=total_revenue,
        pending_deliveries=pending_deliveries,
        recent_sales=recent_sales,
        top_contents=top_contents
    )

@app.route('/catalog')
@login_required
def catalog_view():
    """Visualizar catálogo completo"""
    contents = get_all_active_contents()
    
    # Organizar por categoria
    categorized = {}
    for content in contents:
        category = content.get('category', 'outros')
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(content)
    
    return render_template('catalog.html', categorized=categorized, categories=CATEGORIES)

@app.route('/sales')
@login_required
def sales_view():
    """Visualizar vendas"""
    purchases = load_purchases()
    
    # Filtros
    status_filter = request.args.get('status', 'all')
    
    sales_list = [{"id": pid, **pdata} for pid, pdata in purchases.items()]
    
    if status_filter != 'all':
        sales_list = [s for s in sales_list if s.get('status') == status_filter]
    
    # Ordenar por data (mais recente primeiro)
    sales_list = sorted(sales_list, key=lambda x: x.get('purchased_at', ''), reverse=True)
    
    # Adicionar informações do catálogo
    catalog = load_catalog()
    for sale in sales_list:
        content = catalog.get(sale.get('content_id'), {})
        sale['content_title'] = content.get('title', 'N/A')
    
    return render_template('sales.html', sales=sales_list, status_filter=status_filter)

@app.route('/analytics')
@login_required
def analytics():
    """Página de análises e gráficos"""
    purchases = load_purchases()
    catalog = load_catalog()
    
    # Receita por dia (últimos 30 dias)
    today = datetime.now()
    daily_revenue = {}
    
    for i in range(30):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        daily_revenue[date] = 0
    
    for purchase in purchases.values():
        if purchase.get('status') == 'completed':
            purchase_date = purchase.get('purchased_at', '')[:10]
            if purchase_date in daily_revenue:
                daily_revenue[purchase_date] += purchase.get('amount', 0)
    
    # Vendas por categoria
    category_sales = {cat: 0 for cat in CATEGORIES.keys()}
    category_revenue = {cat: 0 for cat in CATEGORIES.keys()}
    
    for purchase in purchases.values():
        if purchase.get('status') == 'completed':
            content = catalog.get(purchase.get('content_id'), {})
            category = content.get('category', 'outros')
            category_sales[category] = category_sales.get(category, 0) + 1
            category_revenue[category] = category_revenue.get(category, 0) + purchase.get('amount', 0)
    
    return render_template(
        'analytics.html',
        daily_revenue=daily_revenue,
        category_sales=category_sales,
        category_revenue=category_revenue,
        categories=CATEGORIES
    )

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/stats')
@login_required
def api_stats():
    """API para estatísticas em tempo real"""
    catalog = load_catalog()
    purchases = load_purchases()
    
    total_sales = len([p for p in purchases.values() if p.get('status') == 'completed'])
    total_revenue = sum([p.get('amount', 0) for p in purchases.values() if p.get('status') == 'completed'])
    
    return jsonify({
        'total_contents': len([c for c in catalog.values() if c.get('active', True)]),
        'total_sales': total_sales,
        'total_revenue': float(total_revenue),
        'pending_deliveries': len([p for p in purchases.values() if p.get('status') == 'completed' and not p.get('delivered', False)])
    })

# =============================================================================
# SERVIDOR
# =============================================================================

if __name__ == '__main__':
    # Criar pasta de templates se não existir
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

