from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.thread import Thread, Message, Draft, Connection
import uuid
from datetime import datetime

threads_bp = Blueprint('threads', __name__)

def get_user_from_token(token):
    """Extrai usuário do token (mock)"""
    if token and token.startswith('mock_token_'):
        user_id = token.replace('mock_token_', '')
        return User.query.get(user_id)
    return None

@threads_bp.route('/threads', methods=['GET'])
def get_threads():
    """Lista todas as threads do usuário"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Filtros
        channel = request.args.get('channel')  # 'whatsapp', 'telegram', 'instagram'
        status = request.args.get('status')    # 'NEW', 'OPEN', 'DONE'
        search = request.args.get('search')    # Busca por nome ou mensagem
        
        query = Thread.query.filter_by(user_id=user.id)
        
        if channel:
            query = query.filter_by(channel=channel)
        
        if status:
            query = query.filter_by(status=status)
        
        if search:
            query = query.filter(
                db.or_(
                    Thread.contact_name.ilike(f'%{search}%'),
                    Thread.contact_handle.ilike(f'%{search}%')
                )
            )
        
        threads = query.order_by(Thread.last_message_at.desc()).all()
        
        # Adiciona informações extras para cada thread
        threads_data = []
        for thread in threads:
            thread_dict = thread.to_dict()
            
            # Última mensagem
            last_message = Message.query.filter_by(thread_id=thread.id)\
                                      .order_by(Message.sent_at.desc()).first()
            if last_message:
                thread_dict['last_message'] = last_message.body
                thread_dict['last_message_time'] = last_message.sent_at.strftime('%H:%M')
            
            # Contagem de mensagens não lidas (mock)
            unread_count = Message.query.filter_by(
                thread_id=thread.id, 
                direction='IN'
            ).count()
            thread_dict['unread_count'] = unread_count if unread_count > 0 else 0
            thread_dict['unread'] = unread_count > 0
            
            threads_data.append(thread_dict)
        
        return jsonify({'threads': threads_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@threads_bp.route('/threads/<thread_id>/messages', methods=['GET'])
def get_messages(thread_id):
    """Lista mensagens de uma thread específica"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verifica se a thread pertence ao usuário
        thread = Thread.query.filter_by(id=thread_id, user_id=user.id).first()
        if not thread:
            return jsonify({'error': 'Thread não encontrada'}), 404
        
        messages = Message.query.filter_by(thread_id=thread_id)\
                               .order_by(Message.sent_at.asc()).all()
        
        messages_data = [msg.to_dict() for msg in messages]
        
        return jsonify({
            'thread': thread.to_dict(),
            'messages': messages_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@threads_bp.route('/threads/<thread_id>/messages', methods=['POST'])
def send_message(thread_id):
    """Envia uma nova mensagem"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        message_body = data.get('body')
        
        if not message_body:
            return jsonify({'error': 'Conteúdo da mensagem é obrigatório'}), 400
        
        # Verifica se a thread pertence ao usuário
        thread = Thread.query.filter_by(id=thread_id, user_id=user.id).first()
        if not thread:
            return jsonify({'error': 'Thread não encontrada'}), 404
        
        # Cria nova mensagem
        message_id = str(uuid.uuid4())
        message = Message(
            id=message_id,
            thread_id=thread_id,
            channel=thread.channel,
            direction='OUT',
            body=message_body,
            status='SENT'
        )
        
        db.session.add(message)
        
        # Atualiza timestamp da thread
        thread.last_message_at = datetime.utcnow()
        thread.status = 'OPEN'  # Marca como em andamento
        
        db.session.commit()
        
        # Simula envio para API externa
        print(f"[MOCK] Enviando mensagem via {thread.channel}: {message_body}")
        
        return jsonify({
            'message': 'Mensagem enviada com sucesso',
            'data': message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@threads_bp.route('/threads/<thread_id>/status', methods=['PUT'])
def update_thread_status(thread_id):
    """Atualiza status da thread"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['NEW', 'OPEN', 'DONE']:
            return jsonify({'error': 'Status inválido'}), 400
        
        # Verifica se a thread pertence ao usuário
        thread = Thread.query.filter_by(id=thread_id, user_id=user.id).first()
        if not thread:
            return jsonify({'error': 'Thread não encontrada'}), 404
        
        thread.status = new_status
        thread.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Status atualizado com sucesso',
            'thread': thread.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@threads_bp.route('/threads/<thread_id>/draft', methods=['GET', 'POST', 'DELETE'])
def manage_draft(thread_id):
    """Gerencia rascunhos de mensagens"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verifica se a thread pertence ao usuário
        thread = Thread.query.filter_by(id=thread_id, user_id=user.id).first()
        if not thread:
            return jsonify({'error': 'Thread não encontrada'}), 404
        
        if request.method == 'GET':
            # Busca rascunho existente
            draft = Draft.query.filter_by(thread_id=thread_id).first()
            if draft:
                return jsonify({'draft': draft.to_dict()}), 200
            else:
                return jsonify({'draft': None}), 200
        
        elif request.method == 'POST':
            # Salva ou atualiza rascunho
            data = request.get_json()
            content = data.get('content', '')
            
            draft = Draft.query.filter_by(thread_id=thread_id).first()
            
            if draft:
                draft.content = content
                draft.updated_at = datetime.utcnow()
            else:
                draft_id = str(uuid.uuid4())
                draft = Draft(
                    id=draft_id,
                    thread_id=thread_id,
                    content=content
                )
                db.session.add(draft)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Rascunho salvo',
                'draft': draft.to_dict()
            }), 200
        
        elif request.method == 'DELETE':
            # Remove rascunho
            draft = Draft.query.filter_by(thread_id=thread_id).first()
            if draft:
                db.session.delete(draft)
                db.session.commit()
            
            return jsonify({'message': 'Rascunho removido'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

