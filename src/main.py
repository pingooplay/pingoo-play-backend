import os
import sys
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.thread import Thread, Message, Draft, Connection
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.threads import threads_bp
from src.routes.connections import connections_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), \'static\'))
app.config[\'SECRET_KEY\'] = \'asdf#FGSgvasgf$5$WGT\'

# Mova a importação do \'db\' para cá
from src.models.user import db

# Configurar CORS para permitir requisições do frontend
CORS(app, origins=[
    \'http://localhost:5173\', 
    \'http://localhost:3000\',
    \'https://*.vercel.app\',
    \'https://*.netlify.app\',
    \'https://pingooplay.com\',
    \'https://app.pingooplay.com\'
] )

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix=\'/api\')
app.register_blueprint(auth_bp, url_prefix=\'/api/auth\')
app.register_blueprint(threads_bp, url_prefix=\'/api\')
app.register_blueprint(connections_bp, url_prefix=\'/api\')

# Configuração do banco de dados
# Configuração do banco de dados (será definida no bloco if __name__ == \'__main__\':)
app.config[\'SQLALCHEMY_TRACK_MODIFICATIONS\'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route(\'/\', defaults={\'path\': \'\'}) 
@app.route(\'/<path:path>\')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return \
