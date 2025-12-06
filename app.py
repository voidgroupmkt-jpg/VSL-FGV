import os
from flask import Flask, render_template, jsonify, request, redirect, make_response
import hmac

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Constantes do cloaker
COOKIE_NAME = "creative_session"
COOKIE_VALUE = "authorized"
COOKIE_MAX_AGE = 3 * 60 * 60  # 3 horas

# Secrets
TOKEN_OFFER = os.environ.get("TOKEN_OFFER")
BLOCK_URL = os.environ.get("BLOCK_URL", "https://www.gov.br/pt-br")

def is_replit_env():
    """Verificar se está em Replit"""
    return bool(os.environ.get("REPL_ID") or os.environ.get("REPL_SLUG"))

def validate_token(provided, expected):
    """Validar token com timing-safe comparison"""
    if not provided or not expected:
        return False
    try:
        return hmac.compare_digest(str(provided), str(expected))
    except:
        return False

@app.before_request
def cloaker_check():
    """Verificar acesso com cloaker
    Suporta:
    1. ?creative=meta_ads_2025_X9k7f2qR8vUe4ZsB1tL0
    2. ?utm_source=FB&utm_campaign=...&utm_medium=...&creative=meta_ads_2025_X9k7f2qR8vUe4ZsB1tL0
    """
    path = request.path
    
    # Em Replit, permitir acesso livre
    if is_replit_env():
        return None
    
    # Permitir rotas específicas
    if path in ['/debug', '/favicon.ico'] or path.startswith(('/static/', '/api/', '/assets/')):
        return None
    
    # Se tem cookie válido, permitir
    if request.cookies.get(COOKIE_NAME) == COOKIE_VALUE:
        print(f"[CLOAKER] Cookie válido - Acesso permitido")
        return None
    
    # Verificar parâmetro creative (com ou sem UTM)
    creative = request.args.get('creative', '').strip()
    
    # Log dos parâmetros recebidos
    utm_params = {
        'utm_source': request.args.get('utm_source'),
        'utm_campaign': request.args.get('utm_campaign'),
        'utm_medium': request.args.get('utm_medium'),
        'utm_content': request.args.get('utm_content'),
        'utm_term': request.args.get('utm_term'),
    }
    utm_params = {k: v for k, v in utm_params.items() if v}  # Remover None
    
    if creative:
        if TOKEN_OFFER and validate_token(creative, TOKEN_OFFER):
            print(f"[CLOAKER] Token válido - Creative: {creative}")
            if utm_params:
                print(f"[CLOAKER] Parâmetros UTM recebidos: {utm_params}")
            
            # Criar cookie e redirecionar para /
            from flask import Response
            resp = Response()
            resp.status_code = 302
            resp.headers['Location'] = '/'
            resp.set_cookie(COOKIE_NAME, COOKIE_VALUE, max_age=COOKIE_MAX_AGE, httponly=True, samesite='Lax')
            return resp
        else:
            print(f"[CLOAKER] Token inválido - Bloqueando")
            return redirect(BLOCK_URL, code=302)
    
    # Sem token e sem cookie - bloquear
    print(f"[CLOAKER] Acesso bloqueado")
    return redirect(BLOCK_URL, code=302)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug')
def debug():
    """Verificar status do cloaker"""
    return jsonify({
        "environment": "REPLIT" if is_replit_env() else "PRODUCTION",
        "cloaker_active": not is_replit_env(),
        "token_configured": bool(TOKEN_OFFER),
        "block_url_configured": bool(BLOCK_URL)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
