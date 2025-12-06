import os
from flask import Flask, render_template, jsonify, request, redirect
from cloaker import (
    init_cloaker, is_replit_environment, validate_token, 
    set_auth_cookie, get_env_secrets, COOKIE_NAME, COOKIE_VALUE
)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Inicializar cloaker se TOKEN_OFFER ou BLOCK_URL estiverem configurados
token_offer = os.environ.get("TOKEN_OFFER")
block_url = os.environ.get("BLOCK_URL")
if token_offer or block_url:
    init_cloaker(token_offer, block_url)


@app.before_request
def apply_cloaker():
    """Aplicar cloaker antes de cada request"""
    path = request.path
    
    # Se em desenvolvimento (Replit), permitir acesso livre
    if is_replit_environment():
        return None
    
    # Permitir debug endpoint
    if path == '/debug':
        return None
    
    # Ignorar rotas estáticas e API
    if path.startswith(('/static/', '/api/', '/assets/', '/fonts/')) or path in ['/favicon.ico', '/robots.txt']:
        return None
    
    secrets = get_env_secrets()
    token_offer_env = secrets["token_offer"]
    block_url_env = secrets["block_url"]
    
    # Verificar cookie
    if request.cookies.get(COOKIE_NAME) == COOKIE_VALUE:
        print(f"[CLOAKER] Cookie válido - Acesso permitido para: {path}")
        return None
    
    # Verificar parâmetro creative
    creative = request.args.get('creative', '').strip()
    if creative:
        if token_offer_env and validate_token(creative, token_offer_env):
            print(f"[CLOAKER] Token válido - Redirecionando para {path}")
            # Remover o parâmetro creative da URL
            clean_path = path  # path não contém query string
            response = redirect(clean_path, code=302)
            set_auth_cookie(response)
            return response
        else:
            print(f"[CLOAKER] Token inválido")
            if block_url_env:
                return redirect(block_url_env, code=302)
            return "Access Denied", 403
    
    # Bloquear acesso
    print(f"[CLOAKER] Acesso bloqueado para: {path}")
    if block_url_env:
        return redirect(block_url_env, code=302)
    return "Access Denied", 403


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/debug')
def debug():
    """Endpoint de debug para verificar o estado do cloaker"""
    return jsonify({
        "cloaker_active": not is_replit_environment(),
        "token_offer_configured": bool(token_offer),
        "block_url_configured": bool(block_url),
        "environment": "REPLIT" if is_replit_environment() else "PRODUCTION"
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
