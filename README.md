# Findtact

Findtact is a full-stack contact manager with **semantic search**.  
Instead of searching by exact keywords, Findtact lets you search by **meaning/context** by ranking contacts using vector similarity.

**Tech Stack:** React + Vite (frontend), Flask (REST API), PostgreSQL + pgvector (vector search), SQLAlchemy, SentenceTransformer

---
<img width="650" height="850" alt="Screenshot 2026-01-08 at 2 11 40 PM" src="https://github.com/user-attachments/assets/ac2ea9f2-2f9b-48d0-ba8f-e8823df0839d" />


---

## Key Features

- **Contacts CRUD**: create, update, delete contacts with validation (e.g. email format + uniqueness)
- **Paginated listing**: `GET /contacts?page=...&per_page=...`
- **Semantic search**: query contacts by meaning/context and return ranked results with similarity scores
- **Seed demo data**: one-click demo dataset to try semantic search immediately
- **Health check**: DB connectivity endpoint

---

## How Semantic Search Works (High Level)

1. For each contact, Findtact builds a combined text profile (e.g. name, email, tags, notes)
2. A SentenceTransformer model converts the profile into a vector
3. Vectors are stored in PostgreSQL using `pgvector`
4. When you search, the query is embedded and the backend ranks contacts by vector distance in SQL

---

## Project Structure

```text
findtact/
├── frontend/
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── ContactList.jsx
│       ├── ContactForm.jsx
│       └── App.css
├── backend/
│   ├── config.py
│   ├── models.py
│   └── main.py
└── docs/
    └── screenshots/
```
