from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Thread(db.Model):
    __tablename__ = 'threads'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    channel = db.Column(db.String(20), nullable=False)  # 'whatsapp', 'telegram', 'instagram'
    external_thread_id = db.Column(db.String(255), nullable=False)
    contact_name = db.Column(db.String(255), nullable=False)
    contact_handle = db.Column(db.String(255), nullable=False)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='NEW')  # 'NEW', 'OPEN', 'DONE'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    messages = db.relationship('Message', backref='thread', lazy=True, cascade='all, delete-orphan')
    drafts = db.relationship('Draft', backref='thread', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'channel': self.channel,
            'external_thread_id': self.external_thread_id,
            'contact_name': self.contact_name,
            'contact_handle': self.contact_handle,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True)
    thread_id = db.Column(db.String(36), db.ForeignKey('threads.id'), nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    direction = db.Column(db.String(10), nullable=False)  # 'IN', 'OUT'
    body = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(500))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='SENT')  # 'SENT', 'DELIVERED', 'READ', 'FAILED'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'channel': self.channel,
            'direction': self.direction,
            'body': self.body,
            'media_url': self.media_url,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Draft(db.Model):
    __tablename__ = 'drafts'
    
    id = db.Column(db.String(36), primary_key=True)
    thread_id = db.Column(db.String(36), db.ForeignKey('threads.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'content': self.content,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Connection(db.Model):
    __tablename__ = 'connections'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'WA', 'TG', 'IG'
    status = db.Column(db.String(20), default='ACTIVE')  # 'ACTIVE', 'INACTIVE', 'ERROR'
    token_ref = db.Column(db.String(255))  # Referência para token criptografado
    connection_metadata = db.Column(db.JSON)  # Dados específicos da conexão
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'status': self.status,
            'connection_metadata': self.connection_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

