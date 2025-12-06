import os
import hmac
import hashlib
from functools import wraps
from urllib.parse import urlencode, urlparse, parse_qs
from flask import request, redirect, abort

# Tempo de expiração do cookie (3 horas)
COOKIE_MAX_AGE = 3 * 60 * 60  # 10800 segundos
COOKIE_NAME = "creative_session"
COOKIE_VALUE = "authorized"


def get_env_secrets():
    """Obter secrets do ambiente"""
    return {
        "token_offer": os.environ.get("TOKEN_OFFER"),
        "block_url": os.environ.get("BLOCK_URL"),
    }


def is_replit_environment():
    """Verificar se está em ambiente Replit (desenvolvimento)"""
    return bool(os.environ.get("REPL_ID") or os.environ.get("REPL_SLUG"))


def is_ignored_route(path):
    """Verificar se a rota deve ser ignorada pelo cloaker"""
    ignored_prefixes = ["/static/", "/api/", "/assets/", "/fonts/"]
    ignored_exact = ["/favicon.ico", "/robots.txt"]
    
    for prefix in ignored_prefixes:
        if path.startswith(prefix):
            return True
    
    if path in ignored_exact:
        return True
    
    return False


def validate_token(provided_token, expected_token):
    """Validar token usando comparação segura contra timing attacks"""
    if not provided_token or not expected_token:
        return False
    
    try:
        provided_bytes = str(provided_token).encode('utf-8')
        expected_bytes = str(expected_token).encode('utf-8')
        
        # Usar comparação timing-safe
        return hmac.compare_digest(provided_bytes, expected_bytes)
    except Exception:
        return False


def get_creative_param():
    """Extrair parâmetro creative da URL"""
    creative = request.args.get('creative', '').strip()
    return creative


def has_valid_cookie():
    """Verificar se o cookie de sessão é válido"""
    return request.cookies.get(COOKIE_NAME) == COOKIE_VALUE


def create_redirect_without_param(path):
    """Criar redirecionamento removendo o parâmetro creative da URL"""
    # Remover o parâmetro creative da query string
    args = request.args.to_dict()
    args.pop('creative', None)
    
    if args:
        return f"{path}?{urlencode(args)}"
    return path


def set_auth_cookie(response):
    """Definir cookie de autenticação"""
    # Usar secure=True em produção (não em Replit)
    is_production = not is_replit_environment()
    try:
        response.set_cookie(
            COOKIE_NAME,
            COOKIE_VALUE,
            max_age=COOKIE_MAX_AGE,
            httpOnly=True,
            secure=is_production,
            samesite="Lax" if not is_production else "None"
        )
    except Exception as e:
        print(f"[CLOAKER] Erro ao definir cookie: {e}")
    return response


def block_access(block_url, reason):
    """Bloquear acesso redirecionando para BLOCK_URL"""
    print(f"[CLOAKER] Acesso bloqueado - Motivo: {reason}")
    if block_url:
        print(f"[CLOAKER] Redirecionando para: {block_url}")
        return redirect(block_url, code=302)
    else:
        print("[CLOAKER] BLOCK_URL não configurada")
        abort(403)


def init_cloaker(token_offer=None, block_url=None):
    """Inicializar sistema de cloaker"""
    is_replit = is_replit_environment()
    print("[CLOAKER] Sistema de cloaker inicializado")
    
    if is_replit:
        print("[CLOAKER] Ambiente: REPLIT (Desenvolvimento) - Cloaker DESATIVADO para desenvolvimento livre")
    else:
        print("[CLOAKER] Ambiente: PRODUÇÃO - Cloaker ATIVO e bloqueando acessos sem autenticação")
    
    if token_offer:
        print(f"[CLOAKER] TOKEN_OFFER configurado: {token_offer[:8]}...")
    
    if block_url:
        print(f"[CLOAKER] BLOCK_URL configurada: {block_url}")
    
    print(f"[CLOAKER] Cookie válido por: {COOKIE_MAX_AGE}s (3 horas)")


def cloaker_middleware(f):
    """
    Decorator para proteger rotas com cloaker
    
    FLUXO:
    1. Se Replit (REPL_ID/REPL_SLUG): Acesso livre (desenvolvimento)
    2. Se rota ignorada (/api, /assets, etc): Acesso livre
    3. Se cookie válido: Acesso livre
    4. Se parâmetro creative com token correto: Criar cookie e redirecionar
    5. Se parâmetro creative com token incorreto: Bloquear
    6. Sem cookie e sem parâmetro: Bloquear
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            path = request.path
            
            # ETAPA 1: Detectar ambiente Replit
            if is_replit_environment():
                print("[CLOAKER] Detectado ambiente Replit - Modo desenvolvimento: acesso permitido sem autenticação")
                return f(*args, **kwargs)
            
            # ETAPA 2: Verificar rotas ignoradas
            if is_ignored_route(path):
                print(f"[CLOAKER] Rota ignorada: {path} - Acesso permitido")
                return f(*args, **kwargs)
            
            secrets = get_env_secrets()
            token_offer = secrets["token_offer"]
            block_url = secrets["block_url"]
            
            # ETAPA 3: Verificar cookie de sessão
            if has_valid_cookie():
                print(f"[CLOAKER] Cookie válido detectado - Acesso permitido para: {path}")
                return f(*args, **kwargs)
            
            # ETAPA 4: Verificar parâmetro creative
            creative_param = get_creative_param()
            if creative_param:
                # Validar token
                if token_offer and validate_token(creative_param, token_offer):
                    # Token válido - criar cookie e redirecionar sem o parâmetro
                    redirect_url = create_redirect_without_param(path)
                    print(f"[CLOAKER] Token válido - Criando cookie e redirecionando para: {redirect_url}")
                    
                    response = redirect(redirect_url, code=302)
                    return set_auth_cookie(response)
                else:
                    # Token inválido - bloquear
                    return block_access(block_url, "INVALID_TOKEN")
            
            # ETAPA 5: Bloquear acesso não autorizado
            # Sem cookie e sem parâmetro creative - bloquear
            return block_access(block_url, "ACCESS_DENIED - Sem token e sem cookie válido")
        except Exception as e:
            print(f"[CLOAKER] ERRO no middleware: {str(e)}")
            import traceback
            traceback.print_exc()
            return f(*args, **kwargs)
    
    return decorated_function
