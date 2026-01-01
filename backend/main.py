from flask import request, jsonify
from config import app, db
from models import Contact
import re


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


@app.route("/create_contact", methods=["POST"])
def create_contact():
    first_name = request.json.get("firstName")
    last_name = request.json.get("lastName")
    email = request.json.get("email")

    if not first_name or not last_name or not email:
        return (
            jsonify({"message": "You must include a first name, last name and email"}),
            400,
        )
    # Email format validation
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, email):
        return jsonify({"message": "Invalid email format."}), 400

    new_contact = Contact(first_name=first_name, last_name=last_name, email=email)
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)