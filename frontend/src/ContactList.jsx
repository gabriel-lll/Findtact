import React from "react"

const ContactList = ({ contacts, updateContact, updateCallback, page, pages, goToPrev, goToNext, goToPage }) => {
    const onDelete = async (id) => {
        try {
            const options = {
                method: "DELETE"
            }
            const response = await fetch(`http://127.0.0.1:5000/delete_contact/${id}`, options)
            if (response.status === 200) {
                updateCallback()
            } else {
                console.error("Failed to delete")
            }
        } catch (error) {
            alert(error)
        }
    }

    // Render pagination controls
    const renderPagination = () => {
        if (pages <= 1) return null;
        const pageNumbers = [];
        for (let i = 1; i <= pages; i++) {
            pageNumbers.push(
                <button
                    key={i}
                    className={`page-btn${i === page ? ' active' : ''}`}
                    onClick={() => goToPage(i)}
                    disabled={i === page}
                >
                    {i}
                </button>
            );
        }
        return (
            <div className="pagination-controls">
                <button onClick={goToPrev} disabled={page === 1}>Previous</button>
                {pageNumbers}
                <button onClick={goToNext} disabled={page === pages}>Next</button>
                <span className="page-info">Page {page} of {pages}</span>
            </div>
        );
    };

    return (
        <div className="contact-list-container">
            <h2>Contacts</h2>
            {contacts.length === 0 ? (
                <div className="empty-state">
                    <p>No contacts found. Add your first contact!</p>
                </div>
            ) : (
                <>
                <table className="contact-table">
                    <thead>
                        <tr>
                            <th>First Name</th>
                            <th>Last Name</th>
                            <th>Email</th>
                            <th>Tags</th>
                            <th>Notes</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {contacts.map((contact) => (
                            <tr key={contact.id}>
                                <td>{contact.firstName}</td>
                                <td>{contact.lastName}</td>
                                <td>{contact.email}</td>
                                <td>{contact.tags && contact.tags.length > 0 ? contact.tags.join(", ") : ""}</td>
                                <td>{contact.notes}</td>
                                <td>
                                    <button className="table-btn update-btn" onClick={() => updateContact(contact)}>Update</button>
                                    <button className="table-btn delete-btn" onClick={() => onDelete(contact.id)}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {renderPagination()}
                </>
            )}
        </div>
    )
}

export default ContactList