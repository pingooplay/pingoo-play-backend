from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.thread import Thread, Message, Connection
import uuid
import random
import string
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# Simulação de armazenamento temporário para códigos OTP
otp_storage = {}

def generate_otp():
    """Gera um código OTP de 6 dígitos"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_whatsapp(phone, code):
    """Simula envio de OTP via WhatsApp"""
    print(f"[MOCK] Enviando OTP {code} via WhatsApp para {phone}")
    return True

def send_otp_sms(phone, code):
    """Simula envio de OTP via SMS"""
    print(f"[MOCK] Enviando OTP {code} via SMS para {phone}")
    return True

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Envia código OTP para o número fornecido"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        method = data.get('method', 'whatsapp')  # 'whatsapp' ou 'sms'
        
        if not phone:
            return jsonify({'error': 'Número de telefone é obrigatório'}), 400
        
        # Gera código OTP
        otp_code = generate_otp()
        
        # Armazena temporariamente (em produção, usar Redis)
        otp_storage[phone] = {
            'code': otp_code,
            'expires_at': datetime.utcnow() + timedelta(minutes=2),
            'method': method
        }
        
        # Envia OTP
        if method == 'whatsapp':
            success = send_otp_whatsapp(phone, otp_code)
        else:
            success = send_otp_sms(phone, otp_code)
        
        if success:
            return jsonify({
                'message': f'Código enviado via {method}',
                'expires_in': 120  # 2 minutos
            }), 200
        else:
            return jsonify({'error': 'Falha ao enviar código'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verifica código OTP e autentica usuário"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        code = data.get('code')
        
        if not phone or not code:
            return jsonify({'error': 'Telefone e código são obrigatórios'}), 400
        
        # Verifica se existe OTP para este telefone
        if phone not in otp_storage:
            return jsonify({'error': 'Código não encontrado ou expirado'}), 400
        
        otp_data = otp_storage[phone]
        
        # Verifica se o código expirou
        if datetime.utcnow() > otp_data['expires_at']:
            del otp_storage[phone]
            return jsonify({'error': 'Código expirado'}), 400
        
        # Verifica se o código está correto
        if otp_data['code'] != code:
            return jsonify({'error': 'Código inválido'}), 400
        
        # Remove o código usado
        del otp_storage[phone]
        
        # Busca ou cria usuário
        user = User.query.filter_by(phone=phone).first()
        is_first_login = False
        
        if not user:
            # Cria novo usuário
            user_id = str(uuid.uuid4())
            trial_ends_at = datetime.utcnow() + timedelta(days=30)
            
            user = User(
                id=user_id,
                phone=phone,
                name=f'Usuário {phone[-4:]}',
                trial_ends_at=trial_ends_at
            )
            db.session.add(user)
            is_first_login = True
        
        db.session.commit()
        
        return jsonify({
            'message': 'Autenticação realizada com sucesso',
            'user': user.to_dict(),
            'is_first_login': is_first_login,
            'token': f'mock_token_{user.id}'  # Em produção, usar JWT
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Retorna dados do usuário atual (mock)"""
    try:
        # Em produção, extrair do token JWT
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Mock: extrair user_id do token
        if token.startswith('mock_token_'):
            user_id = token.replace('mock_token_', '')
            user = User.query.get(user_id)
            
            if user:
                return jsonify({'user': user.to_dict()}), 200
            else:
                return jsonify({'error': 'Usuário não encontrado'}), 404
        else:
            return jsonify({'error': 'Token inválido'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

