import { useState, useEffect } from "react";
import ContactList from "./ContactList";
import "./App.css";
import ContactForm from "./ContactForm";
import Footer from "./Footer";
import SemanticSearch from "./SemanticSearch";

function App() {
    const [contacts, setContacts] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [currentContact, setCurrentContact] = useState({})
    // Pagination state
    const [page, setPage] = useState(1);
    const [pages, setPages] = useState(1);
    const [perPage] = useState(10);

    // Semantic search state: null => not searching, [] => searched but no results, [...] => results
    const [searchResults, setSearchResults] = useState(null);

    useEffect(() => {
        // While semantic search is active, don't overwrite the displayed list with paginated fetch.
        if (searchResults !== null) return;
        fetchContacts(page);
    }, [page, searchResults]);

    const fetchContacts = async (pageNum = 1) => {
        const response = await fetch(`http://127.0.0.1:5000/contacts?page=${pageNum}&per_page=${perPage}`);
        const data = await response.json();
        setContacts(data.contacts);
        setPage(data.page);
        setPages(data.pages);
    };

    const closeModal = () => {
        setIsModalOpen(false)
        setCurrentContact({})
    }

    const openCreateModal = () => {
        if (!isModalOpen) setIsModalOpen(true)
    }

    const openEditModal = (contact) => {
        if (isModalOpen) return
        setCurrentContact(contact)
        setIsModalOpen(true)
    }

    const onUpdate = () => {
        closeModal()
        // If we're showing semantic search results, refresh them would require re-running the query.
        // For simplicity, exit semantic search and refresh the normal paginated list.
        setSearchResults(null);
        fetchContacts(page)
    }

    // Pagination handlers
    const goToPage = (p) => {
        if (p >= 1 && p <= pages) setPage(p);
    }
    const goToPrev = () => goToPage(page - 1);
    const goToNext = () => goToPage(page + 1);

    const displayedContacts = searchResults !== null ? searchResults : contacts;

    return (
        <>
            <header className="app-header">
                <h1>Contact Manager</h1>
            </header>
            <section className="about-section">
                <h2>About Contact Manager</h2>
                <p>
                    This app helps you manage your contacts efficiently. Soon, you will be able to use AI-powered semantic search to find contacts in a smarter way!
                </p>

                <SemanticSearch onResults={setSearchResults} />
                {searchResults !== null ? (
                    <div style={{ marginTop: '8px', color: '#4a5568', fontSize: '0.95em' }}>
                        Showing semantic search results (ranked). Clear search to return to the full list.
                    </div>
                ) : null}
            </section>
            <ContactList
                contacts={displayedContacts}
                updateContact={openEditModal}
                updateCallback={onUpdate}
                page={page}
                pages={pages}
                goToPrev={goToPrev}
                goToNext={goToNext}
                goToPage={goToPage}
                disablePagination={searchResults !== null}
                showSimilarity={searchResults !== null}
            />
            <button className="primary-btn" onClick={openCreateModal}>Create New Contact</button>
            {isModalOpen && <div className="modal">
                <div className="modal-content">
                    <span className="close" onClick={closeModal}>&times;</span>
                    <ContactForm existingContact={currentContact} updateCallback={onUpdate} />
                </div>
            </div>
            }
            <Footer />
        </>
    );
}

export default App;