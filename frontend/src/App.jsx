import { useState, useEffect } from "react";
import ContactList from "./ContactList";
import "./App.css";
import ContactForm from "./ContactForm";
import Footer from "./Footer";

function App() {
    const [contacts, setContacts] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [currentContact, setCurrentContact] = useState({})
    // Pagination state
    const [page, setPage] = useState(1);
    const [pages, setPages] = useState(1);
    const [perPage] = useState(10);

    useEffect(() => {
        fetchContacts(page);
    }, [page]);

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
        fetchContacts(page)
    }

    // Pagination handlers
    const goToPage = (p) => {
        if (p >= 1 && p <= pages) setPage(p);
    }
    const goToPrev = () => goToPage(page - 1);
    const goToNext = () => goToPage(page + 1);

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
            </section>
            <ContactList
                contacts={contacts}
                updateContact={openEditModal}
                updateCallback={onUpdate}
                page={page}
                pages={pages}
                goToPrev={goToPrev}
                goToNext={goToNext}
                goToPage={goToPage}
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