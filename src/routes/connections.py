from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.thread import Connection, Thread, Message
import uuid
from datetime import datetime

connections_bp = Blueprint('connections', __name__)

def get_user_from_token(token):
    """Extrai usuário do token (mock)"""
    if token and token.startswith('mock_token_'):
        user_id = token.replace('mock_token_', '')
        return User.query.get(user_id)
    return None

@connections_bp.route('/connections', methods=['GET'])
def get_connections():
    """Lista todas as conexões do usuário"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        connections = Connection.query.filter_by(user_id=user.id).all()
        connections_data = [conn.to_dict() for conn in connections]
        
        return jsonify({'connections': connections_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@connections_bp.route('/connections', methods=['POST'])
def create_connection():
    """Cria uma nova conexão com canal"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        connection_type = data.get('type')  # 'WA', 'TG', 'IG'
        token_data = data.get('token')
        metadata = data.get('metadata', {})
        
        if not connection_type or not token_data:
            return jsonify({'error': 'Tipo e token são obrigatórios'}), 400
        
        if connection_type not in ['WA', 'TG', 'IG']:
            return jsonify({'error': 'Tipo de conexão inválido'}), 400
        
        # Verifica se já existe conexão deste tipo
        existing = Connection.query.filter_by(
            user_id=user.id, 
            type=connection_type
        ).first()
        
        if existing:
            return jsonify({'error': 'Conexão deste tipo já existe'}), 400
        
        # Simula validação do token
        if not validate_connection_token(connection_type, token_data):
            return jsonify({'error': 'Token inválido'}), 400
        
        # Cria nova conexão
        connection_id = str(uuid.uuid4())
        connection = Connection(
            id=connection_id,
            user_id=user.id,
            type=connection_type,
            status='ACTIVE',
            token_ref=f'encrypted_{token_data}',  # Em produção, criptografar
            connection_metadata=metadata
        )
        
        db.session.add(connection)
        db.session.commit()
        
        # Simula criação de threads de exemplo
        create_sample_threads(user.id, connection_type)
        
        return jsonify({
            'message': 'Conexão criada com sucesso',
            'connection': connection.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@connections_bp.route('/connections/<connection_id>', methods=['DELETE'])
def delete_connection(connection_id):
    """Remove uma conexão"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        connection = Connection.query.filter_by(
            id=connection_id, 
            user_id=user.id
        ).first()
        
        if not connection:
            return jsonify({'error': 'Conexão não encontrada'}), 404
        
        # Remove threads relacionadas
        Thread.query.filter_by(
            user_id=user.id,
            channel=get_channel_name(connection.type)
        ).delete()
        
        db.session.delete(connection)
        db.session.commit()
        
        return jsonify({'message': 'Conexão removida com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@connections_bp.route('/connections/<connection_id>/test', methods=['POST'])
def test_connection(connection_id):
    """Testa uma conexão existente"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        connection = Connection.query.filter_by(
            id=connection_id, 
            user_id=user.id
        ).first()
        
        if not connection:
            return jsonify({'error': 'Conexão não encontrada'}), 404
        
        # Simula teste da conexão
        test_result = test_channel_connection(connection.type, connection.token_ref)
        
        if test_result['success']:
            connection.status = 'ACTIVE'
            connection.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Conexão testada com sucesso',
                'result': test_result
            }), 200
        else:
            connection.status = 'ERROR'
            connection.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'error': 'Falha no teste de conexão',
                'result': test_result
            }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def validate_connection_token(connection_type, token):
    """Simula validação de token de conexão"""
    # Em produção, fazer chamadas reais para as APIs
    if connection_type == 'WA':
        # Validar token do WhatsApp Business API
        return len(token) > 10
    elif connection_type == 'TG':
        # Validar token do Telegram Bot
        return token.startswith('bot') or len(token) > 10
    elif connection_type == 'IG':
        # Validar token do Instagram
        return len(token) > 10
    return False

def test_channel_connection(connection_type, token_ref):
    """Simula teste de conexão com canal"""
    # Em produção, fazer chamadas reais para as APIs
    return {
        'success': True,
        'message': f'Conexão {connection_type} funcionando corretamente',
        'timestamp': datetime.utcnow().isoformat()
    }

def get_channel_name(connection_type):
    """Converte tipo de conexão para nome do canal"""
    mapping = {
        'WA': 'whatsapp',
        'TG': 'telegram', 
        'IG': 'instagram'
    }
    return mapping.get(connection_type, connection_type.lower())

def create_sample_threads(user_id, connection_type):
    """Cria threads de exemplo para demonstração"""
    channel = get_channel_name(connection_type)
    
    sample_data = {
        'whatsapp': [
            {
                'contact_name': 'João Silva',
                'contact_handle': '+55 11 99999-1234',
                'message': 'Olá! Gostaria de saber mais sobre seus produtos.'
            }
        ],
        'telegram': [
            {
                'contact_name': 'Maria Santos',
                'contact_handle': '@mariasantos',
                'message': 'Obrigada pelo atendimento!'
            }
        ],
        'instagram': [
            {
                'contact_name': 'Pedro Costa',
                'contact_handle': '@pedrocostaoficial',
                'message': 'Quando vocês fazem entrega?'
            }
        ]
    }
    
    if channel in sample_data:
        for sample in sample_data[channel]:
            thread_id = str(uuid.uuid4())
            thread = Thread(
                id=thread_id,
                user_id=user_id,
                channel=channel,
                external_thread_id=f'ext_{thread_id}',
                contact_name=sample['contact_name'],
                contact_handle=sample['contact_handle'],
                status='NEW'
            )
            db.session.add(thread)
            
            # Adiciona mensagem de exemplo
            message_id = str(uuid.uuid4())
            message = Message(
                id=message_id,
                thread_id=thread_id,
                channel=channel,
                direction='IN',
                body=sample['message'],
                status='READ'
            )
            db.session.add(message)
        
        db.session.commit()

