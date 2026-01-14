import { useState } from "react";
import API from "./api";

const SemanticSearch = ({ onResults }) => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const q = query.trim();
    if (!q) {
      // Empty query => clear results and fall back to normal list.
      onResults(null);
      return;
    }

    setLoading(true);
    try {
      // Quick connectivity check so we can surface a useful error if the backend is down.
      const healthResp = await fetch(API.healthDb);
      if (!healthResp.ok) {
        throw new Error(`Backend health check failed (HTTP ${healthResp.status}). Is Flask running?`);
      }

      const resp = await fetch(API.semanticSearch, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, limit: 10 }),
      });

      let data = null;
      try {
        data = await resp.json();
      } catch {
        // Non-JSON error (e.g., HTML error page)
      }

      if (!resp.ok) {
        const msg = data?.message || `Search failed (HTTP ${resp.status}).`;
        setError(msg);
        onResults([]);
        return;
      }

      onResults(data?.results || []);
    } catch (err) {
      // Browser 'TypeError: Load failed' usually means network/CORS/backend not running.
      console.error("Semantic search failed:", err);
      setError(
        `Load failed. This usually means the backend isn't reachable. ` +
          `Make sure the Flask server is running. Details: ${String(err?.message || err)}`
      );
      onResults([]);
    } finally {
      setLoading(false);
    }
  };

  const onClear = () => {
    setQuery("");
    setError("");
    onResults(null);
  };

  return (
    <div style={{ marginTop: "16px" }}>
      <form onSubmit={onSubmit} style={{ display: "flex", gap: "8px" }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Semantic search (e.g. 'works at google', 'soccer friend', 'acme')"
          style={{ flex: 1, padding: "10px" }}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
        <button type="button" onClick={onClear} disabled={loading && !query}>
          Clear
        </button>
      </form>
      {error ? (
        <div style={{ color: "red", marginTop: "8px" }}>{error}</div>
      ) : null}
      <div style={{ color: "#4a5568", marginTop: "6px", fontSize: "0.9em" }}>
        Tip: leave empty and hit Search to return to the full list.
      </div>
    </div>
  );
};

export default SemanticSearch;

