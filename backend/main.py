from flask import request, jsonify, Response
from config import app, db
from models import Contact
import re
import datetime
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
import numpy as np
import pandas as pd
from io import StringIO

# Load the model once at startup
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim vectors


@app.route("/contacts", methods=["GET"])
def get_contacts():
    # Get pagination parameters from query string, with defaults
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Use SQLAlchemy's paginate method (Flask-SQLAlchemy >=3.0)
    pagination = Contact.query.paginate(page=page, per_page=per_page, error_out=False)
    contacts = pagination.items
    json_contacts = list(map(lambda x: x.to_json(), contacts))

    return jsonify({
        "contacts": json_contacts,
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    })


def build_profile_string(first_name, last_name, email, tags, notes):
    tag_str = " ".join(tags) if tags else ""
    return f"{first_name} {last_name} {email or ''} {tag_str} {notes or ''}"


def generate_embedding(profile_string):
    """Generate a normalized embedding using numpy for vector operations."""
    embedding = embedding_model.encode(profile_string)
    # Use numpy to normalize the embedding vector (unit length for cosine similarity)
    embedding_np = np.array(embedding)
    norm = np.linalg.norm(embedding_np)
    if norm > 0:
        embedding_np = embedding_np / norm
    return embedding_np.tolist(), "all-MiniLM-L6-v2"


@app.route("/create_contact", methods=["POST"])
def create_contact():
    first_name = request.json.get("firstName")
    last_name = request.json.get("lastName")
    email = request.json.get("email")
    tags = request.json.get("tags")
    notes = request.json.get("notes")

    if not first_name or not last_name or not email:
        return (
            jsonify({"message": "You must include a first name, last name and email"}),
            400,
        )
    # Email format validation
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, email):
        return jsonify({"message": "Invalid email format."}), 400

    profile_string = build_profile_string(first_name, last_name, email, tags, notes)
    embedding, embedding_model = generate_embedding(profile_string)
    embedded_at = datetime.datetime.now(datetime.UTC)

    new_contact = Contact(
        first_name=first_name,
        last_name=last_name,
        email=email,
        tags=tags,
        notes=notes,
        search_text=profile_string,
        embedding=embedding,
        embedding_model=embedding_model,
        embedded_at=embedded_at
    )
    try:
        db.session.add(new_contact)
        db.session.commit()
    except Exception as e:
        if 'UNIQUE constraint failed' in str(e) or 'duplicate key value violates unique constraint' in str(e):
            return jsonify({"message": "A contact with this email already exists."}), 400
        return jsonify({"message": str(e)}), 400

    return jsonify({"message": "User created!"}), 201


@app.route("/update_contact/<int:user_id>", methods=["PATCH"])
def update_contact(user_id):
    contact = Contact.query.get(user_id)

    if not contact:
        return jsonify({"message": "User not found"}), 404

    data = request.json
    new_email = data.get("email", contact.email)
    # Email format validation
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if new_email and not re.match(email_regex, new_email):
        return jsonify({"message": "Invalid email format."}), 400
    # Check for duplicate email if changed
    if new_email != contact.email:
        existing = Contact.query.filter_by(email=new_email).first()
        if existing:
            return jsonify({"message": "A contact with this email already exists."}), 400
    contact.first_name = data.get("firstName", contact.first_name)
    contact.last_name = data.get("lastName", contact.last_name)
    contact.email = new_email
    contact.tags = data.get("tags", contact.tags)
    contact.notes = data.get("notes", contact.notes)
    contact.search_text = build_profile_string(contact.first_name, contact.last_name, contact.email, contact.tags, contact.notes)
    contact.embedding, contact.embedding_model = generate_embedding(contact.search_text)
    contact.embedded_at = datetime.datetime.now(datetime.UTC)
    db.session.commit()

    return jsonify({"message": "Usr updated."}), 200


@app.route("/delete_contact/<int:user_id>", methods=["DELETE"])
def delete_contact(user_id):
    contact = Contact.query.get(user_id)

    if not contact:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(contact)
    db.session.commit()

    return jsonify({"message": "User deleted!"}), 200


@app.route("/health/db", methods=["GET"])
def health_db():
    """Quick sanity check for debugging: confirms DB connectivity and row counts."""
    # DB name and user help spot 'wrong database' issues instantly.
    meta = db.session.execute(text("SELECT current_database() AS db, current_user AS user")).mappings().one()
    count = db.session.execute(text("SELECT COUNT(*) AS n FROM public.contact")).mappings().one()["n"]
    return jsonify({"database": meta["db"], "user": meta["user"], "contact_count": count})


@app.errorhandler(Exception)
def handle_unexpected_error(err):
    # Ensure we return JSON on unexpected errors (makes frontend debugging easier).
    # Flask-CORS should attach headers; this handler keeps the response consistent.
    app.logger.exception("Unhandled exception: %s", err)
    return jsonify({"message": str(err)}), 500


@app.route("/semantic_search", methods=["OPTIONS"])
def semantic_search_options():
    # Explicit preflight response. Flask-CORS usually handles this, but some setups
    # can still fail when the main handler errors.
    return ("", 204)


@app.route("/semantic_search", methods=["POST"])
def semantic_search():
    app.logger.info("/semantic_search Origin=%s", request.headers.get("Origin"))
    data = request.get_json() or {}
    query = data.get("query")
    limit = data.get("limit", 10)
    try:
        limit = int(limit)
    except Exception:
        limit = 10
    limit = max(1, min(limit, 50))

    if not query or not str(query).strip():
        return jsonify({"message": "Query is required."}), 400

    query_embedding, _ = generate_embedding(query)

    # Send as pgvector text literal to avoid psycopg2 treating it as numeric[]
    query_embedding_literal = "[" + ",".join(map(str, query_embedding)) + "]"

    sql = text('''
        SELECT
            id,
            first_name,
            last_name,
            email,
            tags,
            notes,
            search_text,
            embedding_model,
            embedded_at,
            (1 - (embedding <=> CAST(:query_embedding AS vector))) AS similarity
        FROM public.contact
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:query_embedding AS vector)
        LIMIT :limit
    ''')

    rows = db.session.execute(
        sql,
        {"query_embedding": query_embedding_literal, "limit": limit}
    ).mappings().all()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "firstName": r["first_name"],
            "lastName": r["last_name"],
            "email": r["email"],
            "tags": r["tags"],
            "notes": r["notes"],
            "search_text": r["search_text"],
            "embedding_model": r["embedding_model"],
            "embedded_at": r["embedded_at"],
            "similarity": float(r["similarity"]) if r["similarity"] is not None else None,
        })

    return jsonify({"results": results})


@app.route("/seed_contacts", methods=["POST"])
def seed_contacts():
    """Seed the database with some dummy contacts for demo/testing.

    Safe to call multiple times: uses email as a natural unique key and will skip
    contacts that already exist.
    """
    dummy_contacts = [
        {
            "firstName": "Maya",
            "lastName": "Thompson",
            "email": "maya.thompson@example.com",
            "tags": ["neighbor", "kids"],
            "notes": "Lives in Apt 3B. Great for package drop-offs. Has a golden retriever named Sunny.",
        },
        {
            "firstName": "Jordan",
            "lastName": "Reed",
            "email": "jordan.reed@example.com",
            "tags": ["coworker", "project"],
            "notes": "Works on the marketing team. Preferred contact: email. Usually free after 3pm.",
        },
        {
            "firstName": "Elena",
            "lastName": "Garcia",
            "email": "elena.garcia@example.com",
            "tags": ["doctor", "clinic"],
            "notes": "Primary care clinic. Front desk asks for DOB when scheduling. Best to call mornings.",
        },
        {
            "firstName": "Sam",
            "lastName": "Patel",
            "email": "sam.patel@example.com",
            "tags": ["landlord", "repairs"],
            "notes": "Building manager. Text for urgent repairs (leaks, heating). Email for paperwork.",
        },
        {
            "firstName": "Renee",
            "lastName": "Kim",
            "email": "renee.kim@example.com",
            "tags": ["friend", "gym"],
            "notes": "Gym buddy. Likes weekend classes and coffee after. Try searching 'gym weekend coffee'.",
        },
    ]

    created = 0
    skipped = 0

    for c in dummy_contacts:
        if Contact.query.filter_by(email=c["email"]).first():
            skipped += 1
            continue

        profile_string = build_profile_string(
            c["firstName"],
            c["lastName"],
            c["email"],
            c.get("tags"),
            c.get("notes"),
        )
        embedding, embedding_model_name = generate_embedding(profile_string)

        new_contact = Contact(
            first_name=c["firstName"],
            last_name=c["lastName"],
            email=c["email"],
            tags=c.get("tags"),
            notes=c.get("notes"),
            search_text=profile_string,
            embedding=embedding,
            embedding_model=embedding_model_name,
            embedded_at=datetime.datetime.now(datetime.UTC),
        )
        db.session.add(new_contact)
        created += 1

    db.session.commit()

    return jsonify({
        "message": "Seed complete.",
        "created": created,
        "skipped": skipped,
        "total": len(dummy_contacts),
    }), 200


# ===================== PANDAS-POWERED ENDPOINTS =====================

@app.route("/export_contacts", methods=["GET"])
def export_contacts():
    """Export all contacts to CSV using pandas DataFrame."""
    contacts = Contact.query.all()

    if not contacts:
        return jsonify({"message": "No contacts to export."}), 404

    # Convert contacts to pandas DataFrame
    data = []
    for c in contacts:
        data.append({
            "id": c.id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "tags": ";".join(c.tags) if c.tags else "",  # Join tags with semicolon
            "notes": c.notes or "",
            "created_at": c.embedded_at
        })

    df = pd.DataFrame(data)

    # Convert to CSV string
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=contacts_export.csv"}
    )


@app.route("/import_contacts", methods=["POST"])
def import_contacts():
    """Import contacts from CSV file using pandas."""
    if "file" not in request.files:
        return jsonify({"message": "No file provided."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No file selected."}), 400

    try:
        # Read CSV into pandas DataFrame
        df = pd.read_csv(file)

        # Validate required columns
        required_cols = ["first_name", "last_name", "email"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({"message": f"Missing required columns: {missing_cols}"}), 400

        # Clean data using pandas
        df = df.fillna("")  # Replace NaN with empty strings
        df["first_name"] = df["first_name"].astype(str).str.strip()
        df["last_name"] = df["last_name"].astype(str).str.strip()
        df["email"] = df["email"].astype(str).str.strip().str.lower()

        created = 0
        skipped = 0
        errors = []

        for idx, row in df.iterrows():
            # Skip if email already exists
            if Contact.query.filter_by(email=row["email"]).first():
                skipped += 1
                continue

            # Parse tags from semicolon-separated string
            tags = []
            if "tags" in row and row["tags"]:
                tags = [t.strip() for t in str(row["tags"]).split(";") if t.strip()]

            notes = row.get("notes", "") if "notes" in df.columns else ""

            profile_string = build_profile_string(
                row["first_name"],
                row["last_name"],
                row["email"],
                tags,
                notes
            )
            embedding, embedding_model_name = generate_embedding(profile_string)

            new_contact = Contact(
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                tags=tags if tags else None,
                notes=notes if notes else None,
                search_text=profile_string,
                embedding=embedding,
                embedding_model=embedding_model_name,
                embedded_at=datetime.datetime.now(datetime.UTC),
            )
            db.session.add(new_contact)
            created += 1

        db.session.commit()

        return jsonify({
            "message": "Import complete.",
            "created": created,
            "skipped": skipped,
            "total_rows": len(df)
        }), 200

    except Exception as e:
        return jsonify({"message": f"Error processing CSV: {str(e)}"}), 400


@app.route("/contacts/analytics", methods=["GET"])
def contacts_analytics():
    """Get analytics about contacts using pandas and numpy."""
    contacts = Contact.query.all()

    if not contacts:
        return jsonify({"message": "No contacts for analytics."}), 404

    # Build DataFrame for analysis
    data = []
    embeddings = []
    for c in contacts:
        data.append({
            "id": c.id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "tags": c.tags or [],
            "notes": c.notes or "",
            "notes_length": len(c.notes) if c.notes else 0,
            "tag_count": len(c.tags) if c.tags else 0,
            "embedded_at": c.embedded_at
        })
        if c.embedding:
            embeddings.append(c.embedding)

    df = pd.DataFrame(data)

    # Tag frequency analysis using pandas
    all_tags = []
    for tags in df["tags"]:
        all_tags.extend(tags)
    tag_series = pd.Series(all_tags)
    tag_counts = tag_series.value_counts().to_dict() if all_tags else {}

    # Notes statistics using pandas/numpy
    notes_stats = {
        "avg_length": float(df["notes_length"].mean()),
        "max_length": int(df["notes_length"].max()),
        "min_length": int(df["notes_length"].min()),
        "contacts_with_notes": int((df["notes_length"] > 0).sum())
    }

    # Tag statistics
    tag_stats = {
        "avg_tags_per_contact": float(df["tag_count"].mean()),
        "max_tags": int(df["tag_count"].max()),
        "contacts_with_tags": int((df["tag_count"] > 0).sum()),
        "unique_tags": len(tag_counts),
        "top_tags": dict(list(tag_counts.items())[:10])  # Top 10 tags
    }

    # Embedding analysis using numpy (if embeddings exist)
    embedding_stats = {}
    if embeddings:
        embeddings_np = np.array(embeddings)
        # Calculate average embedding magnitude
        magnitudes = np.linalg.norm(embeddings_np, axis=1)
        embedding_stats = {
            "total_embedded": len(embeddings),
            "avg_magnitude": float(np.mean(magnitudes)),
            "embedding_dimension": embeddings_np.shape[1]
        }

    return jsonify({
        "total_contacts": len(contacts),
        "notes_stats": notes_stats,
        "tag_stats": tag_stats,
        "embedding_stats": embedding_stats,
        "email_domains": df["email"].str.split("@").str[1].value_counts().to_dict()
    })


@app.route("/contacts/similar/<int:contact_id>", methods=["GET"])
def find_similar_contacts(contact_id):
    """Find contacts similar to a given contact using numpy cosine similarity."""
    contact = Contact.query.get(contact_id)

    if not contact:
        return jsonify({"message": "Contact not found."}), 404

    if not contact.embedding:
        return jsonify({"message": "Contact has no embedding."}), 400

    limit = request.args.get("limit", 5, type=int)
    limit = max(1, min(limit, 20))

    # Get all other contacts with embeddings
    other_contacts = Contact.query.filter(
        Contact.id != contact_id,
        Contact.embedding.isnot(None)
    ).all()

    if not other_contacts:
        return jsonify({"results": [], "message": "No other contacts to compare."})

    # Use numpy for efficient similarity calculation
    target_embedding = np.array(contact.embedding)

    similarities = []
    for c in other_contacts:
        other_embedding = np.array(c.embedding)
        # Cosine similarity using numpy dot product (embeddings are normalized)
        similarity = float(np.dot(target_embedding, other_embedding))
        similarities.append({
            "contact": c.to_json(),
            "similarity": similarity
        })

    # Sort by similarity (descending) using numpy-style sorting
    similarities.sort(key=lambda x: x["similarity"], reverse=True)

    return jsonify({
        "source_contact": contact.to_json(),
        "similar_contacts": similarities[:limit]
    })


# Create database tables on startup (works with both direct run and gunicorn)
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)