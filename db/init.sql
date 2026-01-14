-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- The Contact table will be created by Flask-SQLAlchemy on first run
-- This file just ensures pgvector is ready
