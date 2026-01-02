from config import db
from sqlalchemy.dialects.postgresql import ARRAY

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    tags = db.Column(ARRAY(db.String), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def to_json(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'tags': self.tags,
            'notes': self.notes
        }