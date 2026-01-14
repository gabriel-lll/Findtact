import React, { useEffect, useRef, useState } from "react"
import API from "./api";

const clampOverflow = (el) => {
    if (!el) return false;
    return el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1;
};

const ExpandableCell = ({ id, value, titlePrefix, className = "" }) => {
    const [expanded, setExpanded] = useState(false);
    const [overflow, setOverflow] = useState(false);
    const ref = useRef(null);

    const measure = () => {
        if (!ref.current) return;
        setOverflow(clampOverflow(ref.current));
    };

    useEffect(() => {
        measure();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [value]);

    useEffect(() => {
        const onResize = () => measure();
        window.addEventListener('resize', onResize);
        return () => window.removeEventListener('resize', onResize);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <>
            <div
                ref={ref}
                className={expanded ? `cell-expandable-expanded ${className}` : `cell-expandable ${className}`}
                title={titlePrefix ? `${titlePrefix}: ${value || ''}` : (value || '')}
            >
                {value}
            </div>
            {overflow ? (
                <button
                    type="button"
                    className="cell-toggle"
                    onClick={() => setExpanded((v) => !v)}
                >
                    {expanded ? "Show less" : "Show more"}
                </button>
            ) : null}
        </>
    );
};

const ContactList = ({ contacts, updateContact, updateCallback, page, pages, goToPrev, goToNext, goToPage, disablePagination = false }) => {
    const [expandedNotes, setExpandedNotes] = useState(() => new Set());

    // Tracks which rows have notes that are actually truncated in the UI.
    const [notesOverflow, setNotesOverflow] = useState(() => ({}));
    const notesRefs = useRef({});

    const toggleNotes = (id) => {
        setExpandedNotes((prev) => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    // Measure whether the clamped notes text is overflowing.
    // We do this after render and whenever contacts change.
    useEffect(() => {
        const next = {};
        for (const c of contacts) {
            const el = notesRefs.current[c.id];
            if (!el) continue;
            // If scrollHeight > clientHeight, the text is being clipped.
            next[c.id] = el.scrollHeight > el.clientHeight + 1;
        }
        setNotesOverflow(next);
    }, [contacts]);

    // Re-measure on window resize (column widths can change).
    useEffect(() => {
        const onResize = () => {
            const next = {};
            for (const c of contacts) {
                const el = notesRefs.current[c.id];
                if (!el) continue;
                next[c.id] = el.scrollHeight > el.clientHeight + 1;
            }
            setNotesOverflow(next);
        };
        window.addEventListener('resize', onResize);
        return () => window.removeEventListener('resize', onResize);
    }, [contacts]);

    const onDelete = async (id) => {
        try {
            const options = {
                method: "DELETE"
            }
            const response = await fetch(API.deleteContact(id), options)
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
        if (disablePagination) return null;
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
                            <th className="col-first">First Name</th>
                            <th className="col-last">Last Name</th>
                            <th className="col-email">Email</th>
                            <th className="col-tags">Tags</th>
                            <th className="col-notes">Notes</th>
                            <th className="col-actions">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {contacts.map((contact) => {
                            const isExpanded = expandedNotes.has(contact.id);
                            const notes = contact.notes || "";
                            const showNotesToggle = !!notesOverflow[contact.id];
                            const tagsText = contact.tags && contact.tags.length > 0 ? contact.tags.join(", ") : "";

                            return (
                                <tr key={contact.id}>
                                    <td className="cell-wrap">
                                        <ExpandableCell id={`fn-${contact.id}`} value={contact.firstName || ""} titlePrefix="First name" />
                                    </td>
                                    <td className="cell-wrap">
                                        <ExpandableCell id={`ln-${contact.id}`} value={contact.lastName || ""} titlePrefix="Last name" />
                                    </td>
                                    <td className="cell-wrap">
                                        <ExpandableCell id={`em-${contact.id}`} value={contact.email || ""} titlePrefix="Email" className="cell-mono" />
                                    </td>
                                    <td className="cell-wrap">
                                        <ExpandableCell id={`tg-${contact.id}`} value={tagsText} titlePrefix="Tags" />
                                    </td>
                                    <td className={isExpanded ? "cell-notes-expanded" : "cell-notes"}>
                                        <div
                                            className="notes-content"
                                            title={notes}
                                            ref={(el) => {
                                                if (el) notesRefs.current[contact.id] = el;
                                            }}
                                        >
                                            {notes}
                                        </div>

                                        {showNotesToggle ? (
                                            <button
                                                type="button"
                                                className="notes-toggle"
                                                onClick={() => toggleNotes(contact.id)}
                                            >
                                                {isExpanded ? "Show less" : "Show more"}
                                            </button>
                                        ) : null}
                                    </td>
                                    <td className="col-actions">
                                        <button className="table-btn update-btn" onClick={() => updateContact(contact)}>Update</button>
                                        <button className="table-btn delete-btn" onClick={() => onDelete(contact.id)}>Delete</button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
                {renderPagination()}
                </>
            )}
        </div>
    )
}

export default ContactList