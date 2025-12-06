import os
from flask import Flask, render_template
from cloaker import cloaker_middleware, init_cloaker

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Inicializar cloaker se TOKEN_OFFER ou BLOCK_URL estiverem configurados
token_offer = os.environ.get("TOKEN_OFFER")
block_url = os.environ.get("BLOCK_URL")
if token_offer or block_url:
    init_cloaker(token_offer, block_url)

@app.route('/')
@cloaker_middleware
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
