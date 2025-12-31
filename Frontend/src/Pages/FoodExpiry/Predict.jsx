// src/Pages/FoodExpiry/Predict.jsx
import React, { useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { predictExpiry } from "../../api/foodApi.js";
import {
  validateRequired,
  validatePositiveNumber,
  validateDate,
} from "./validation.js";
import "./foodexpiry.css";

const STORAGE_OPTIONS = ["fridge", "freezer", "pantry"];

export default function Predict() {
  const [form, setForm] = useState({
    userId: "demo-user",
    item_name: "",
    item_category: "",
    purchase_date: "",
    quantity: 1,
    storage_type: "fridge",
    used_before_expiry: false,
  });

  const [errors, setErrors] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  function validate() {
    const newErr = {};
    const e1 = validateRequired(form.userId, "User ID");
    if (e1) newErr.userId = e1;

    const e2 = validateRequired(form.item_name, "Item name");
    if (e2) newErr.item_name = e2;

    const e3 = validateRequired(form.item_category, "Item category");
    if (e3) newErr.item_category = e3;

    const e4 = validateDate(form.purchase_date, "Purchase date");
    if (e4) newErr.purchase_date = e4;

    const e5 = validatePositiveNumber(form.quantity, "Quantity");
    if (e5) newErr.quantity = e5;

    if (!STORAGE_OPTIONS.includes(form.storage_type)) {
      newErr.storage_type = "Invalid storage type";
    }

    setErrors(newErr);
    return Object.keys(newErr).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setResult(null);
    setApiError("");

    if (!validate()) return;

    try {
      setLoading(true);
      const payload = {
        userId: form.userId,
        item_name: form.item_name,
        item_category: form.item_category,
        purchase_date: form.purchase_date,
        quantity: Number(form.quantity),
        storage_type: form.storage_type,
        used_before_expiry: form.used_before_expiry,
      };

      const data = await predictExpiry(payload);
      setResult(data);
    } catch (err) {
      setApiError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fe-layout">
      <Sidebar />
      <div className="fe-main">
        <Topbar title="Predict Expiry" />

        <div className="fe-main__content">
          <div className="fe-grid fe-grid--2">
            <form className="fe-card fe-form" onSubmit={handleSubmit}>
              <h2 className="fe-section__title mb-4">Prediction Input</h2>

              <div className="fe-form__group">
                <label>User ID</label>
                <input
                  type="text"
                  name="userId"
                  value={form.userId}
                  onChange={handleChange}
                />
                {errors.userId && (
                  <span className="fe-form__error">{errors.userId}</span>
                )}
              </div>

              <div className="fe-form__group">
                <label>Item Name</label>
                <input
                  type="text"
                  name="item_name"
                  value={form.item_name}
                  onChange={handleChange}
                  placeholder="e.g. milk, kottu, mango"
                />
                {errors.item_name && (
                  <span className="fe-form__error">{errors.item_name}</span>
                )}
              </div>

              <div className="fe-form__group">
                <label>Item Category</label>
                <input
                  type="text"
                  name="item_category"
                  value={form.item_category}
                  onChange={handleChange}
                  placeholder="dairy, fruit, snack..."
                />
                {errors.item_category && (
                  <span className="fe-form__error">{errors.item_category}</span>
                )}
              </div>

              <div className="fe-form__group">
                <label>Purchase Date (YYYY-MM-DD)</label>
                <input
                  type="date"
                  name="purchase_date"
                  value={form.purchase_date}
                  onChange={handleChange}
                />
                {errors.purchase_date && (
                  <span className="fe-form__error">{errors.purchase_date}</span>
                )}
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
                {errors.storage_type && (
                  <span className="fe-form__error">
                    {errors.storage_type}
                  </span>
                )}
              </div>

              <div className="fe-form__group fe-form__group--inline">
                <label>
                  <input
                    type="checkbox"
                    name="used_before_expiry"
                    checked={form.used_before_expiry}
                    onChange={handleChange}
                  />
                  &nbsp; Usually used before expiry?
                </label>
              </div>

              {apiError && (
                <div className="fe-alert fe-alert--error mt-3">
                  {apiError}
                </div>
              )}

              <button
                className="fe-btn fe-btn--primary mt-4"
                type="submit"
                disabled={loading}
              >
                {loading ? "Predicting..." : "Predict Expiry"}
              </button>
            </form>

            <div className="fe-card">
              <h2 className="fe-section__title mb-4">Prediction Result</h2>
              {!result && <p>No prediction yet. Submit the form.</p>}

              {result && (
                <div className="fe-result-box">
                  <p>
                    <strong>Item:</strong> {result.item_name}
                  </p>
                  <p>
                    <strong>Category:</strong> {result.category}
                  </p>
                  <p>
                    <strong>Model Days:</strong>{" "}
                    {result.model_final_days ?? "—"}
                  </p>
                  <p>
                    <strong>AED Adjusted Days:</strong>{" "}
                    {result.aed_adjusted_days ?? "—"}
                  </p>
                  <p>
                    <strong>Predicted Expiry Date:</strong>{" "}
                    {result.predicted_expiry_date || "—"}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
