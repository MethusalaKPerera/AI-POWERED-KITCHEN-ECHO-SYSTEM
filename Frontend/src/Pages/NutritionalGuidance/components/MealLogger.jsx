// src/Pages/NutritionalGuidance/Components/MealLogger.jsx

import React, { useEffect, useMemo, useState } from "react";
import { addIntake, searchFoods, DEFAULT_USER_ID } from "../../../services/nutritionApi";
import "./MealLogger.css";

// Helper: today YYYY-MM-DD
function todayStr() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export default function MealLogger({ userId = DEFAULT_USER_ID }) {
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
    const basis = selected.serving_basis || "serving";
    const grams = selected.serving_size_g ? ` • ${selected.serving_size_g}g` : "";
    return `${selected.food_name} (${basis}${grams})`;
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
        user_id: userId || DEFAULT_USER_ID,
        food_id: selected?.food_id || "",
        food_name: selected?.food_name || query.trim(),
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
    <div className="ml-wrap">
      <div className="ml-hero">
        <div>
          <h2 className="ml-title">Meal Logger</h2>
          <p className="ml-subtitle">
            Search a food, select it, enter quantity and date, then save your intake.
          </p>
        </div>

        <div className="ml-meta">
          <div className="ml-pill">
            User: <b>{userId || DEFAULT_USER_ID}</b>
          </div>
        </div>
      </div>

      <form onSubmit={onSubmit} className="ml-card">
        <div className="ml-grid">
          {/* Food search */}
          <div className="ml-field ml-food">
            <label className="ml-label">Food</label>
            <div className="ml-inputWrap">
              <input
                className="ml-input"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setSelected(null);
                }}
                placeholder={placeholder}
              />

              {loading && <div className="ml-inlineHint">Searching…</div>}

              {suggestions.length > 0 && (
                <div className="ml-dropdown">
                  {suggestions.map((it) => (
                    <button
                      type="button"
                      key={it.food_id || it.food_name}
                      className="ml-item"
                      onClick={() => onPick(it)}
                    >
                      <div className="ml-itemTop">
                        <span className="ml-itemName">{it.food_name}</span>
                        {it.food_id ? <span className="ml-id">ID: {it.food_id}</span> : null}
                      </div>
                      <div className="ml-itemSub">
                        {(it.serving_basis || "serving")}
                        {it.serving_size_g ? ` • ${it.serving_size_g}g` : ""}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Date */}
          <div className="ml-field">
            <label className="ml-label">Date</label>
            <input
              className="ml-input"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>

          {/* Quantity */}
          <div className="ml-field">
            <label className="ml-label">Quantity (servings)</label>
            <input
              className="ml-input"
              type="number"
              step="0.25"
              min="0.25"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
          </div>
        </div>

        {error && <div className="ml-alert ml-error">{error}</div>}
        {success && <div className="ml-alert ml-ok">{success}</div>}

        <div className="ml-actions">
          <button type="submit" className="ml-btn" disabled={saving}>
            {saving ? "Saving..." : "Add Intake"}
          </button>

          <div className="ml-tip">
            Tip: Logging meals improves the accuracy of your deficiency analysis.
          </div>
        </div>
      </form>
    </div>
  );
}
