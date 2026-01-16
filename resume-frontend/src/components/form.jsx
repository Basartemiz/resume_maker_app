import React, { useEffect, useState } from "react";
import originalData from "/src/media/user.json"; // one-time load from src

const STORAGE_KEY = "user_profile_json";

export default function JsonLocalEditor({ title = "User Profile Editor" }) {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);

  // Load from localStorage or fallback to src/media/user.json
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setData(JSON.parse(saved));
      } else {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(originalData));
        setData(originalData);
      }
    } catch (err) {
      console.error("Error loading JSON:", err);
      setData(originalData);
    } finally {
      setLoading(false);
    }
  }, []);

  // Save changes to localStorage immediately
  const handleChange = (key, value) => {
    const updated = { ...data, [key]: value };
    setData(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    setStatus("Saved to local storage ✓");
    setTimeout(() => setStatus(""), 1000);
  };

  // Reset to original JSON
  const handleReset = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(originalData));
    setData(originalData);
    setStatus("Reset to original file");
    setTimeout(() => setStatus(""), 1000);
  };

  if (loading) return <div className="p-4 text-muted">Loading JSON…</div>;
  if (!data) return <div className="p-4 text-danger">Failed to load JSON.</div>;

  return (
    <div className="container py-4">
      <h3 className="mb-3">{title}</h3>

      <div className="card shadow-sm">
        <div className="card-body">
          {Object.keys(data).map((key) => (
            <div key={key} className="mb-3">
              <label className="form-label fw-semibold">{key}</label>

              <input
                type="text"
                className="form-control"
                value={data[key] ?? ""}
                onChange={(e) => handleChange(key, e.target.value)}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="d-flex justify-content-between align-items-center mt-3">
        <button className="btn btn-outline-danger" onClick={handleReset}>
          Reset to Original
        </button>
        {status && <div className="text-success small">{status}</div>}
      </div>
    </div>
  );
}
