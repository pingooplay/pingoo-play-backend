import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.thread import Thread, Message, Draft, Connection
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.threads import threads_bp
from src.routes.connections import connections_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

from src.models.user import db

# Configurar CORS para permitir requisições do frontend
CORS(app, origins=[
    'http://localhost:5173', 
    'http://localhost:3000',
    'https://*.vercel.app',
    'https://*.netlify.app',
    'https://pingooplay.com',
    'https://app.pingooplay.com'
])

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(threads_bp, url_prefix='/api')
app.register_blueprint(connections_bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return {'status': 'ok', 'message': 'Pingoo Play API funcionando'}, 200

if __name__ == '__main__':
    import os
    
    # Configurar banco de dados para produção
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Render PostgreSQL
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Desenvolvimento local
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    
    # Recriar tabelas com nova configuração
    with app.app_context():
        db.create_all()
    
    # Configurar porta para produção
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
