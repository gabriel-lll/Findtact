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
    const [perPage] = useState(5);

    // Semantic search state: null => not searching, [] => searched but no results, [...] => results
    const [searchResults, setSearchResults] = useState(null);

    // Seeder UI state
    const [seeding, setSeeding] = useState(false);
    const [seedMessage, setSeedMessage] = useState("");

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

    const seedDemoContacts = async () => {
        setSeedMessage("");
        setSeeding(true);
        try {
            const resp = await fetch("http://127.0.0.1:5000/seed_contacts", { method: "POST" });
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok) {
                setSeedMessage(data?.message || `Seeding failed (HTTP ${resp.status}).`);
                return;
            }

            const created = data?.created ?? 0;
            const skipped = data?.skipped ?? 0;
            setSeedMessage(`Seeded demo contacts. Created ${created}, skipped ${skipped}.`);

            // Exit semantic search mode (if active), reset to page 1, and refresh.
            setSearchResults(null);
            setPage(1);
            await fetchContacts(1);
        } catch (e) {
            setSeedMessage(`Seeding failed: ${String(e)}`);
        } finally {
            setSeeding(false);
        }
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
                <h1>Findtact</h1>
            </header>
            <section className="about-section">
                <h2>About Findtact</h2>
                <p>
                    Save people you meet in everyday life (neighbors, coworkers, a landlord, a doctor) with helpful tags and notes.
                    Semantic search lets you find someone by context, not just exact words.
                    Try searches like "package drop-off", "building manager", "marketing team", "gym buddy", "primary care clinic", or "neighbor in Apt 3B".
                </p>

                <div style={{ display: "flex", justifyContent: "center", gap: "10px", flexWrap: "wrap", marginTop: "12px" }}>
                    <button className="primary-btn" style={{ margin: 0 }} onClick={seedDemoContacts} disabled={seeding}>
                        {seeding ? "Seeding…" : "Seed demo contacts"}
                    </button>
                </div>
                {seedMessage ? (
                    <div style={{ marginTop: "10px", color: "#4a5568", fontSize: "0.95em" }}>
                        {seedMessage}
                    </div>
                ) : null}

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

