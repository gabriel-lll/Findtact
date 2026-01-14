# Findtact

Findtact is a full-stack contact manager with **semantic search**.  
Instead of searching by exact keywords, Findtact lets you search by **meaning/context** by ranking contacts using vector similarity.

**Tech Stack:** React + Vite (frontend), Flask (REST API), PostgreSQL + pgvector (vector search), SQLAlchemy, SentenceTransformer

---
<img width="650" height="850" alt="Screenshot 2026-01-08 at 2 11 40 PM" src="https://github.com/user-attachments/assets/ac2ea9f2-2f9b-48d0-ba8f-e8823df0839d" />


---

## 🚀 Quick Start (Docker)

The easiest way to try Findtact is with Docker Compose. This starts the entire stack (PostgreSQL + pgvector, Flask backend, React frontend) with one command.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2+)

### Run with Docker Compose

```bash
# Clone the repository
git clone https://github.com/gabriel-lll/Findtact.git
cd Findtact

# Copy environment file (optional - defaults work fine)
cp .env.example .env

# Start all services
docker compose up --build

# Wait for all services to be healthy (~30-60 seconds for model download on first run)
```

Once running, open your browser:

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:5000](http://localhost:5000)

### First Steps

1. Click **"Seed demo contacts"** to add sample data
2. Try semantic searches like:
   - "package drop-off"
   - "building manager"
   - "marketing team"
   - "gym buddy"
   - "primary care clinic"

### Stop the app

```bash
docker compose down

# To also remove the database volume:
docker compose down -v
```

---

## 🛠️ Local Development Setup

For development, you can run the frontend and backend separately with hot-reloading.

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL 15+ with pgvector extension

### Database Setup

```bash
# Install PostgreSQL with pgvector (macOS)
brew install postgresql@16 pgvector

# Start PostgreSQL
brew services start postgresql@16

# Create database and enable pgvector
psql postgres -c "CREATE DATABASE findtact;"
psql findtact -c "CREATE EXTENSION vector;"
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL="postgresql://localhost:5432/findtact"

# Run the Flask server (development mode)
python main.py
```

The backend will be available at [http://localhost:5000](http://localhost:5000)

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173)

---

## ✨ Key Features

- **Contacts CRUD**: Create, update, delete contacts with validation (e.g., email format + uniqueness)
- **Paginated listing**: `GET /contacts?page=...&per_page=...`
- **Semantic search**: Query contacts by meaning/context and return ranked results with similarity scores
- **Seed demo data**: One-click demo dataset to try semantic search immediately
- **Health check**: DB connectivity endpoint at `/health/db`

---

## 🔍 How Semantic Search Works

1. For each contact, Findtact builds a combined text profile (name, email, tags, notes)
2. A SentenceTransformer model (`all-MiniLM-L6-v2`) converts the profile into a 384-dimension vector
3. Vectors are stored in PostgreSQL using the `pgvector` extension
4. When you search, the query is embedded and the backend ranks contacts by vector distance using cosine similarity

---

## 📁 Project Structure

```text
findtact/
├── docker-compose.yml       # Production-ready Docker setup
├── .env.example             # Environment variables template
├── db/
│   └── init.sql             # PostgreSQL initialization script
├── frontend/
│   ├── Dockerfile           # Production frontend image
│   ├── nginx.conf           # Nginx reverse proxy config
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── api.js           # Centralized API configuration
│       ├── App.jsx
│       ├── ContactList.jsx
│       ├── ContactForm.jsx
│       ├── SemanticSearch.jsx
│       └── App.css
└── backend/
    ├── Dockerfile           # Production backend image
    ├── requirements.txt
    ├── config.py            # Flask configuration
    ├── models.py            # SQLAlchemy models
    └── main.py              # Flask routes and API
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/contacts?page=1&per_page=10` | List contacts (paginated) |
| POST | `/create_contact` | Create a new contact |
| PATCH | `/update_contact/<id>` | Update an existing contact |
| DELETE | `/delete_contact/<id>` | Delete a contact |
| POST | `/semantic_search` | Search contacts by meaning |
| POST | `/seed_contacts` | Seed demo contacts |
| GET | `/health/db` | Database health check |

### Example: Semantic Search

```bash
curl -X POST http://localhost:5000/semantic_search \
  -H "Content-Type: application/json" \
  -d '{"query": "gym buddy", "limit": 5}'
```

Response:

```json
{
  "results": [
    {
      "id": 5,
      "firstName": "Renee",
      "lastName": "Kim",
      "email": "renee.kim@example.com",
      "tags": ["friend", "gym"],
      "notes": "Gym buddy. Likes weekend classes...",
      "similarity": 0.72
    }
  ]
}
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://findtact:findtact123@db:5432/findtact` | PostgreSQL connection string |
| `FLASK_ENV` | `production` | Flask environment (`development` or `production`) |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Comma-separated allowed CORS origins |
| `VITE_API_URL` | `/api` | API base URL for frontend (use `/api` in production) |
| `POSTGRES_USER` | `findtact` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `findtact123` | PostgreSQL password |
| `POSTGRES_DB` | `findtact` | PostgreSQL database name |

---

## 🚢 Production Deployment

The Docker Compose setup is production-ready with:

- **Gunicorn** WSGI server for the Flask backend
- **Nginx** serving the React build with API reverse proxy
- **Health checks** for all services
- **Persistent volume** for PostgreSQL data
- **Non-root users** in containers for security

### Deploy to a Server

```bash
# On your server
git clone https://github.com/gabriel-lll/Findtact.git
cd Findtact

# Configure environment
cp .env.example .env
# Edit .env with secure passwords

# Start in detached mode
docker compose up -d --build

# View logs
docker compose logs -f
```

---

## 📝 License

MIT License - feel free to use this project for learning or as a starting point for your own apps!
