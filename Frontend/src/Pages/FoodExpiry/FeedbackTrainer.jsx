// src/Pages/FoodExpiry/FeedbackTrainer.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { getAllFoods, sendFeedback } from "../../api/foodApi.js";
import { validatePositiveNumber } from "./validation.js";
import "./foodExpiry.css";

export default function FeedbackTrainer() {
  const [foods, setFoods] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [form, setForm] = useState({
    userId: "demo-user",
    feedback: "on_time",
    actual_days: "",
  });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const data = await getAllFoods();
        setFoods(data || []);
      } catch (err) {
        setApiError(err.message);
      }
    }
    load();
  }, []);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function validate() {
    const newErr = {};
    if (!selectedId) newErr.foodId = "Select a food item";
    if (!form.userId) newErr.userId = "User ID is required";

    const daysErr = validatePositiveNumber(form.actual_days, "Actual days");
    if (daysErr) newErr.actual_days = daysErr;

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
        foodId: selectedId,
        userId: form.userId,
        feedback: form.feedback,
        actual_days: Number(form.actual_days),
      };
      const data = await sendFeedback(payload);
      setSuccess(
        `Feedback recorded. New adjustment for '${data.category}' = ${data.new_adjustment}`
      );
      setForm((prev) => ({ ...prev, actual_days: "" }));
    } catch (err) {
      setApiError(err.message);
    }
  }

  return (
    <div className="fe-layout">
      <Sidebar />
      <div className="fe-main">
        <Topbar title="Feedback Trainer (AED)" />
        <div className="fe-main__content">
          <form className="fe-card fe-form fe-form--medium" onSubmit={handleSubmit}>
            <h2 className="fe-section__title mb-4">Label a Completed Item</h2>

            <div className="fe-form__group">
              <label>Saved Food Item</label>
              <select
                value={selectedId}
                onChange={(e) => setSelectedId(e.target.value)}
              >
                <option value="">-- Select from inventory --</option>
                {foods.map((f) => (
                  <option key={f._id} value={f._id}>
                    {f.foodName || f.itemName} ({f.category}) – predicted{" "}
                    {f.predictedExpiryDate || "N/A"}
                  </option>
                ))}
              </select>
              {errors.foodId && (
                <span className="fe-form__error">{errors.foodId}</span>
              )}
            </div>

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
              <label>Feedback Type</label>
              <select
                name="feedback"
                value={form.feedback}
                onChange={handleChange}
              >
                <option value="early">Spoiled earlier than predicted</option>
                <option value="on_time">Prediction was correct</option>
                <option value="late">
                  Stayed fresh longer than predicted
                </option>
              </select>
            </div>

            <div className="fe-form__group">
              <label>Actual days until spoilage</label>
              <input
                type="number"
                name="actual_days"
                min="1"
                value={form.actual_days}
                onChange={handleChange}
              />
              {errors.actual_days && (
                <span className="fe-form__error">{errors.actual_days}</span>
              )}
            </div>

            {apiError && (
              <div className="fe-alert fe-alert--error mt-3">{apiError}</div>
            )}
            {success && (
              <div className="fe-alert fe-alert--success mt-3">{success}</div>
            )}

            <button className="fe-btn fe-btn--primary mt-4" type="submit">
              Submit Feedback
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
