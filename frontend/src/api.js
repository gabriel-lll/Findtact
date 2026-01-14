// API configuration
// In development: uses Vite proxy or direct backend URL
// In production: uses relative /api path (nginx proxy)

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export const API = {
  contacts: `${API_BASE_URL}/contacts`,
  createContact: `${API_BASE_URL}/create_contact`,
  updateContact: (id) => `${API_BASE_URL}/update_contact/${id}`,
  deleteContact: (id) => `${API_BASE_URL}/delete_contact/${id}`,
  semanticSearch: `${API_BASE_URL}/semantic_search`,
  seedContacts: `${API_BASE_URL}/seed_contacts`,
  healthDb: `${API_BASE_URL}/health/db`,
};

export default API;
