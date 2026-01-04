// src/Pages/FoodExpiry/AddFood.jsx
import React, { useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { addFood } from "../../api/foodApi.js";
import {
  validateRequired,
  validatePositiveNumber,
  validateDate,
} from "./validation.js";
import "./foodexpiry.css";

export default function AddFood() {
  const [form, setForm] = useState({
    userId: "demo-user",
    foodName: "",
    item_name: "",
    item_category: "",
    purchase_date: "",
    quantity: 1,
    storage_type: "fridge",
    used_before_expiry: false,
  });

  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [success, setSuccess] = useState("");

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
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
        purchase_date: "",
      }));
    } catch (err) {
      setApiError(err.message);
    }
  }

  return (
    <div className="fe-layout">
      <Sidebar />
      <div className="fe-main">
        <Topbar title="Add Food & Store Prediction" />
        <div className="fe-main__content">
          <form className="fe-card fe-form fe-form--wide" onSubmit={handleSubmit}>
            <div className="fe-form__grid">
              <div>
                <h2 className="fe-section__title mb-4">Basic Details</h2>

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
                  <input
                    type="text"
                    name="item_name"
                    value={form.item_name}
                    onChange={handleChange}
                    placeholder="kottu, milk, banana..."
                  />
                  {errors.item_name && (
                    <span className="fe-form__error">{errors.item_name}</span>
                  )}
                </div>

                <div className="fe-form__group">
                  <label>Category</label>
                  <input
                    type="text"
                    name="item_category"
                    value={form.item_category}
                    onChange={handleChange}
                    placeholder="dairy, snack, fruit..."
                  />
                  {errors.item_category && (
                    <span className="fe-form__error">
                      {errors.item_category}
                    </span>
                  )}
                </div>
              </div>

              <div>
                <h2 className="fe-section__title mb-4">Storage & Purchase</h2>

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
              Save Item & Prediction
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
