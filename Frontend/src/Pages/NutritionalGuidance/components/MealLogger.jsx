// src/Pages/NutritionalGuidance/Components/MealLogger.jsx

import React, { useEffect, useMemo, useState } from "react";
import { addIntake, searchFoods } from "../../../services/nutritionApi";

// Helper: today YYYY-MM-DD
function todayStr() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export default function MealLogger({ userId = "demo" }) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [selected, setSelected] = useState(null);

  const [date, setDate] = useState(todayStr());
  const [quantity, setQuantity] = useState(1);

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Debounced search
  useEffect(() => {
    let t = null;

    async function run() {
      setError("");
      setSuccess("");

      const q = query.trim();
      if (q.length < 2) {
        setSuggestions([]);
        return;
      }

      setLoading(true);
      try {
        const res = await searchFoods(q, 15);
        setSuggestions(res?.items || []);
      } catch (e) {
        setError(e.message || "Search failed");
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }

    t = setTimeout(run, 300);
    return () => clearTimeout(t);
  }, [query]);

  const placeholder = useMemo(() => {
    if (!selected) return "Type a food name (e.g., Tea, Rice, Egg)";
    return `${selected.food_name} (${selected.serving_basis || ""}${selected.serving_size_g ? `, ${selected.serving_size_g}g` : ""
      })`;
  }, [selected]);

  const onPick = (item) => {
    setSelected(item);
    setQuery(item.food_name);
    setSuggestions([]);
    setSuccess("");
    setError("");
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!selected?.food_id && !selected?.food_name) {
      setError("Please select a food from the dropdown list.");
      return;
    }
    if (!date) {
      setError("Please choose a date.");
      return;
    }
    const q = Number(quantity);
    if (!Number.isFinite(q) || q <= 0) {
      setError("Quantity must be a number greater than 0.");
      return;
    }

    setSaving(true);
    try {
      const payload = {
        user_id: userId,
        food_id: selected.food_id || "",
        food_name: selected.food_name || query.trim(),
        quantity: q,
        date: date,
      };

      const res = await addIntake(payload);
      setSuccess(res?.message || "Intake added!");

      // reset for next log
      setSelected(null);
      setQuery("");
      setSuggestions([]);
      setQuantity(1);
    } catch (e2) {
      setError(e2.message || "Failed to add intake");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ maxWidth: 720 }}>
      <h2 style={{ marginBottom: 10 }}>Meal Logger</h2>
      <p style={{ marginTop: 0, opacity: 0.8 }}>
        Search a food, select it, enter quantity and date, then save your intake.
      </p>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
        <div style={{ position: "relative" }}>
          <label style={{ display: "block", marginBottom: 6 }}>Food</label>
          <input
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelected(null);
            }}
            placeholder={placeholder}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 10,
              border: "1px solid #cbd5e1",
              outline: "none",
            }}
          />

          {loading && (
            <div style={{ marginTop: 6, fontSize: 13, opacity: 0.75 }}>
              Searching...
            </div>
          )}

          {suggestions.length > 0 && (
            <div
              style={{
                position: "absolute",
                zIndex: 50,
                top: "100%",
                left: 0,
                right: 0,
                background: "white",
                border: "1px solid #e2e8f0",
                borderRadius: 10,
                marginTop: 6,
                maxHeight: 260,
                overflowY: "auto",
                boxShadow: "0 10px 25px rgba(0,0,0,0.08)",
              }}
            >
              {suggestions.map((it) => (
                <div
                  key={it.food_id || it.food_name}
                  onClick={() => onPick(it)}
                  style={{
                    padding: "10px 12px",
                    cursor: "pointer",
                    borderBottom: "1px solid #f1f5f9",
                  }}
                >
                  <div style={{ fontWeight: 600 }}>{it.food_name}</div>
                  <div style={{ fontSize: 12, opacity: 0.75 }}>
                    {it.food_id ? `ID: ${it.food_id} • ` : ""}
                    {it.serving_basis || "serving"}
                    {it.serving_size_g ? ` • ${it.serving_size_g}g` : ""}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div>
            <label style={{ display: "block", marginBottom: 6 }}>Date</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 10,
                border: "1px solid #cbd5e1",
                outline: "none",
              }}
            />
          </div>

          <div>
            <label style={{ display: "block", marginBottom: 6 }}>
              Quantity (servings)
            </label>
            <input
              type="number"
              step="0.25"
              min="0.25"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 10,
                border: "1px solid #cbd5e1",
                outline: "none",
              }}
            />
          </div>
        </div>

        {error && (
          <div
            style={{
              color: "#b91c1c",
              background: "#fee2e2",
              padding: 10,
              borderRadius: 10,
            }}
          >
            {error}
          </div>
        )}
        {success && (
          <div
            style={{
              color: "#065f46",
              background: "#d1fae5",
              padding: 10,
              borderRadius: 10,
            }}
          >
            {success}
          </div>
        )}

        <button
          type="submit"
          disabled={saving}
          style={{
            padding: "10px 14px",
            borderRadius: 12,
            border: "none",
            cursor: saving ? "not-allowed" : "pointer",
            fontWeight: 700,
          }}
        >
          {saving ? "Saving..." : "Add Intake"}
        </button>
      </form>
    </div>
  );
}
