from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    plan = db.Column(db.String(20), default='TRIAL')  # 'TRIAL', 'BASIC', 'PRO'
    trial_started_at = db.Column(db.DateTime, default=datetime.utcnow)
    trial_ends_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    threads = db.relationship('Thread', backref='user', lazy=True)
    connections = db.relationship('Connection', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.phone}>'

    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'email': self.email,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'plan': self.plan,
            'trial_started_at': self.trial_started_at.isoformat() if self.trial_started_at else None,
            'trial_ends_at': self.trial_ends_at.isoformat() if self.trial_ends_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
