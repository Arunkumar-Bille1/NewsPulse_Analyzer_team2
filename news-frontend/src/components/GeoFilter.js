// src/components/GeoFilter.js
import React, { useEffect, useState } from "react";

function GeoFilter({ articles = [], onFilterChange }) {
  const [countries, setCountries] = useState([]);
  const [selected, setSelected] = useState("");

  useEffect(() => {
    const list = [
      ...new Set(
        (articles || [])
          .map((a) => (a.country ? String(a.country).trim() : ""))
          .filter((c) => c !== "")
      ),
    ].sort();
    setCountries(list);
  }, [articles]);

  useEffect(() => {
    // automatically apply filter on change
    if (!selected) {
      onFilterChange(articles || []);
    } else {
      const filtered = (articles || []).filter(
        (a) => a.country && String(a.country).trim() === selected
      );
      onFilterChange(filtered);
    }
  }, [selected, articles, onFilterChange]);

  return (
    <div style={styles.container}>
      <label style={styles.label}>📍 Filter by Country</label>
      <select
        value={selected}
        onChange={(e) => setSelected(e.target.value)}
        style={styles.select}
      >
        <option value="">All Countries ({articles.length})</option>
        {countries.map((c, i) => (
          <option key={i} value={c}>
            {c} ({articles.filter((a) => a.country && String(a.country).trim() === c).length})
          </option>
        ))}
      </select>

      {!countries.length && (
        <p style={styles.noLocations}>No geo-tagged locations found</p>
      )}
    </div>
  );
}

const styles = {
  container: {
    padding: "12px",
    backgroundColor: "#fff",
    borderRadius: "10px",
    boxShadow: "0 4px 18px rgba(20,24,38,0.04)",
  },
  label: {
    display: "block",
    fontSize: "14px",
    fontWeight: "700",
    marginBottom: "8px",
    color: "#333",
  },
  select: {
    width: "100%",
    padding: "10px 12px",
    borderRadius: "8px",
    border: "1px solid #e6e6e9",
    fontSize: "14px",
    backgroundColor: "#fff",
    cursor: "pointer",
  },
  noLocations: {
    marginTop: "10px",
    color: "#7b7b7b",
    fontSize: "13px",
  },
};

export default GeoFilter;
