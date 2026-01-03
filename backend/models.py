from config import db
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import TIMESTAMP
from pgvector.sqlalchemy import Vector

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    tags = db.Column(ARRAY(db.String), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    # Embedding fields for semantic search
    search_text = db.Column(db.Text, nullable=True)  # Combined profile string for embedding
    embedding = db.Column(Vector(1536), nullable=True)  # Adjust dimension as needed
    embedding_model = db.Column(db.Text, nullable=True)
    embedded_at = db.Column(TIMESTAMP, nullable=True)

    def to_json(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'tags': self.tags,
            'notes': self.notes,
            'search_text': self.search_text,
            'embedding_model': self.embedding_model,
            'embedded_at': self.embedded_at
        }