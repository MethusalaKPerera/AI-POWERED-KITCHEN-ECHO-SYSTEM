// src/Pages/FoodExpiry/AddFood.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { addFood } from "../../api/foodApi.js";
import {
  validateRequired,
  validatePositiveNumber,
  validateDate,
} from "./validation.js";
import "./foodexpiry.css";
import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

function nextUserId() {
  const key = "FE_LAST_USER_ID_NUM";
  const last = Number(localStorage.getItem(key) || "0");
  const next = last + 1;
  localStorage.setItem(key, String(next));
  return `U${String(next).padStart(3, "0")}`; // U001, U002...
}

export default function AddFood() {
  const [form, setForm] = useState({
    userId: "U001",
    foodName: "",
    item_name: "",
    item_category: "",
    purchase_date: "",
    printed_expiry_date: "", // ✅ new
    quantity: 1,
    storage_type: "fridge",
    used_before_expiry: false,
  });

  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [success, setSuccess] = useState("");

  // dropdown options
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [itemOptions, setItemOptions] = useState([]);
  const [categoryOptions, setCategoryOptions] = useState([]);

  async function loadOptions() {
    try {
      setOptionsLoading(true);
      const res = await axios.get(`${BASE_URL}/api/food/options`);
      setItemOptions(res.data?.items || []);
      setCategoryOptions(res.data?.categories || []);
    } catch (e) {
      // If options endpoint isn't ready yet, user can still type manually
      setItemOptions([]);
      setCategoryOptions([]);
    } finally {
      setOptionsLoading(false);
    }
  }

  useEffect(() => {
    // initialize with a generated ID for demo
    const stored = localStorage.getItem("FE_DEMO_USER_ID");
    if (!stored) {
      const gen = nextUserId();
      localStorage.setItem("FE_DEMO_USER_ID", gen);
      setForm((p) => ({ ...p, userId: gen }));
    } else {
      setForm((p) => ({ ...p, userId: stored }));
    }

    loadOptions();
  }, []);

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  function generateUserId() {
    const gen = nextUserId();
    localStorage.setItem("FE_DEMO_USER_ID", gen);
    setForm((p) => ({ ...p, userId: gen }));
  }

  function validate() {
    const newErr = {};
    const req = ["userId", "foodName", "item_name", "item_category"];
    req.forEach((field) => {
      const err = validateRequired(form[field], field.replace("_", " "));
      if (err) newErr[field] = err;
    });

    const dErr = validateDate(form.purchase_date, "Purchase date");
    if (dErr) newErr.purchase_date = dErr;

    // optional printed expiry date validation (only if filled)
    if (form.printed_expiry_date) {
      const peErr = validateDate(form.printed_expiry_date, "Printed expiry date");
      if (peErr) newErr.printed_expiry_date = peErr;
    }

    const qErr = validatePositiveNumber(form.quantity, "Quantity");
    if (qErr) newErr.quantity = qErr;

    setErrors(newErr);
    return Object.keys(newErr).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setApiError("");
    setSuccess("");

    if (!validate()) return;

    try {
      const payload = {
        userId: form.userId,
        foodName: form.foodName,
        item_name: form.item_name,
        item_category: form.item_category,
        purchase_date: form.purchase_date,
        printed_expiry_date: form.printed_expiry_date || null, // ✅ send to backend
        quantity: Number(form.quantity),
        storage_type: form.storage_type,
        used_before_expiry: form.used_before_expiry,
      };

      const data = await addFood(payload);
      setSuccess(`Saved: ${data.food.foodName || data.food.itemName}`);

      setForm((prev) => ({
        ...prev,
        foodName: "",
        item_name: "",
        item_category: "",
        purchase_date: "",
        printed_expiry_date: "",
        quantity: 1,
        storage_type: "fridge",
        used_before_expiry: false,
      }));
    } catch (err) {
      setApiError(err.message);
    }
  }

  return (
    <div className="fe-layout">
      <Sidebar />
      <div className="fe-main">
        <Topbar title="Add Food" />
        <div className="fe-main__content">
          <form className="fe-card fe-form fe-form--wide" onSubmit={handleSubmit}>
            <div className="fe-form__grid">
              <div>
                <h2 className="fe-section__title mb-4">Basic Details</h2>

                <div className="fe-form__group">
                  <label>User ID (per-user personalization)</label>
                  <div style={{ display: "flex", gap: 10 }}>
                    <input
                      type="text"
                      name="userId"
                      value={form.userId}
                      onChange={(e) => {
                        handleChange(e);
                        localStorage.setItem("FE_DEMO_USER_ID", e.target.value);
                      }}
                      placeholder="U001"
                    />
                    <button
                      type="button"
                      className="fe-btn fe-btn--ghost"
                      onClick={generateUserId}
                      title="Generate a new unique user ID"
                    >
                      Generate
                    </button>
                  </div>
                  {errors.userId && (
                    <span className="fe-form__error">{errors.userId}</span>
                  )}
                  <div className="fe-muted fe-small">
                    Each User ID has its own feedback history and personalized predictions.
                  </div>
                </div>

                <div className="fe-form__group">
                  <label>Food Name (friendly)</label>
                  <input
                    type="text"
                    name="foodName"
                    value={form.foodName}
                    onChange={handleChange}
                    placeholder="E.g. Leftover chicken curry"
                  />
                  {errors.foodName && (
                    <span className="fe-form__error">{errors.foodName}</span>
                  )}
                </div>

                <div className="fe-form__group">
                  <label>Item Name (model)</label>

                  {itemOptions.length > 0 ? (
                    <select
                      name="item_name"
                      value={form.item_name}
                      onChange={handleChange}
                      disabled={optionsLoading}
                    >
                      <option value="">Select an item...</option>
                      {itemOptions.map((it) => (
                        <option key={it} value={it}>
                          {it}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="text"
                      name="item_name"
                      value={form.item_name}
                      onChange={handleChange}
                      placeholder="milk, banana, chicken_breast..."
                    />
                  )}

                  {errors.item_name && (
                    <span className="fe-form__error">{errors.item_name}</span>
                  )}
                  <div className="fe-muted fe-small">
                    Shows only items supported by the trained model (prevents unknown item errors).
                  </div>
                </div>

                <div className="fe-form__group">
                  <label>Category</label>

                  {categoryOptions.length > 0 ? (
                    <select
                      name="item_category"
                      value={form.item_category}
                      onChange={handleChange}
                      disabled={optionsLoading}
                    >
                      <option value="">Select a category...</option>
                      {categoryOptions.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="text"
                      name="item_category"
                      value={form.item_category}
                      onChange={handleChange}
                      placeholder="dairy, meat, fruit..."
                    />
                  )}

                  {errors.item_category && (
                    <span className="fe-form__error">{errors.item_category}</span>
                  )}
                </div>
              </div>

              <div>
                <h2 className="fe-section__title mb-4">Storage & Dates</h2>

                <div className="fe-form__group">
                  <label>Purchase Date</label>
                  <input
                    type="date"
                    name="purchase_date"
                    value={form.purchase_date}
                    onChange={handleChange}
                  />
                  {errors.purchase_date && (
                    <span className="fe-form__error">
                      {errors.purchase_date}
                    </span>
                  )}
                </div>

                <div className="fe-form__group">
                  <label>Printed Expiry Date (optional)</label>
                  <input
                    type="date"
                    name="printed_expiry_date"
                    value={form.printed_expiry_date}
                    onChange={handleChange}
                  />
                  {errors.printed_expiry_date && (
                    <span className="fe-form__error">
                      {errors.printed_expiry_date}
                    </span>
                  )}
                  <div className="fe-muted fe-small">
                    If provided, the system will never predict beyond the printed expiry (safety cap).
                  </div>
                </div>

                <div className="fe-form__group">
                  <label>Quantity</label>
                  <input
                    type="number"
                    name="quantity"
                    min="1"
                    value={form.quantity}
                    onChange={handleChange}
                  />
                  {errors.quantity && (
                    <span className="fe-form__error">{errors.quantity}</span>
                  )}
                </div>

                <div className="fe-form__group">
                  <label>Storage Type</label>
                  <select
                    name="storage_type"
                    value={form.storage_type}
                    onChange={handleChange}
                  >
                    <option value="fridge">Fridge</option>
                    <option value="freezer">Freezer</option>
                    <option value="pantry">Pantry</option>
                  </select>
                </div>

                <div className="fe-form__group fe-form__group--inline">
                  <label>
                    <input
                      type="checkbox"
                      name="used_before_expiry"
                      checked={form.used_before_expiry}
                      onChange={handleChange}
                    />
                    &nbsp; This item is usually finished before it expires
                  </label>
                </div>
              </div>
            </div>

            {apiError && (
              <div className="fe-alert fe-alert--error mt-4">{apiError}</div>
            )}
            {success && (
              <div className="fe-alert fe-alert--success mt-4">{success}</div>
            )}

            <button className="fe-btn fe-btn--primary mt-6" type="submit">
              Save Item
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
