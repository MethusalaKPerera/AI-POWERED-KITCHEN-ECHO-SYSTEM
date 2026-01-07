import React, { useEffect, useMemo, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { getAllFoods, sendFeedback } from "../../api/foodApi.js";
import { validatePositiveNumber } from "./validation.js";
import "./foodexpiry.css";

function normalizeFood(f) {
  return {
    _id: f._id,
    // show readable name
    label: `${(f.foodName || f.itemName || f.item_name || "Item")} (${f.category || f.item_category || "unknown"})`,
    category: f.category || f.item_category || "",
    item_name: (f.itemName || f.item_name || "").toString(),
    predictedExpiryDate:
      f.finalExpiryDate ||
      f.predictedExpiryDate ||
      f.predicted_expiry_date ||
      "",
    userId: f.userId || f.user_id || "", // optional display
  };
}

export default function FeedbackTrainer() {
  const [foods, setFoods] = useState([]);
  const [selectedId, setSelectedId] = useState("");

  // ✅ MUST MATCH AddFood.jsx key
  const defaultUser = localStorage.getItem("FE_DEMO_USER_ID") || "U001";

  const [form, setForm] = useState({
    userId: defaultUser,
    feedback: "early",
    actual_days: "",
  });

  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const data = await getAllFoods();
        setFoods((Array.isArray(data) ? data : []).map(normalizeFood));
      } catch (err) {
        setApiError(err.message);
      }
    }
    load();
  }, []);

  // ✅ keep in sync if FE_DEMO_USER_ID changes elsewhere (AddFood Generate button)
  useEffect(() => {
    const onStorage = () => {
      const u = localStorage.getItem("FE_DEMO_USER_ID");
      if (u) setForm((p) => ({ ...p, userId: u }));
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const selectedFood = useMemo(
    () => foods.find((f) => f._id === selectedId),
    [foods, selectedId]
  );

  function handleChange(e) {
    const { name, value } = e.target;

    setForm((prev) => ({ ...prev, [name]: value }));

    // ✅ keep same key everywhere in FoodExpiry module
    if (name === "userId") localStorage.setItem("FE_DEMO_USER_ID", value);
  }

  function validate() {
    const newErr = {};
    if (!selectedId) newErr.foodId = "Select a food item";
    if (!form.userId?.trim()) newErr.userId = "User ID is required";

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
        userId: form.userId.trim(), // ✅ remove spaces
        feedback: form.feedback, // early / on_time / late
        actual_days: Number(form.actual_days),
      };

      const data = await sendFeedback(payload);

      // ✅ Use new backend response keys (per-item counter)
      const minReq = data.min_required_feedback ?? 5;
      const countAfter = data.item_feedback_count_after ?? 0;
      const needed = data.feedback_needed ?? Math.max(0, minReq - countAfter);
      const activatedNow = !!data.personalization_activated_now;

      if (activatedNow) {
        setSuccess(
          `✅ Feedback saved. Personalization is now ACTIVATED for this item (${countAfter}/${minReq}).`
        );
      } else {
        setSuccess(
          `✅ Feedback saved (${countAfter}/${minReq}). Submit ${needed} more feedback(s) for this SAME item to activate personalization.`
        );
      }

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
            <h2 className="fe-section__title mb-3">Label a Completed Item</h2>

            <div className="fe-muted mb-4">
              Choose an item and submit feedback. After <strong>5 feedbacks for the same item</strong>,
              the system will apply personalization for that item.
            </div>

            <div className="fe-form__group">
              <label>Saved Food Item</label>
              <select value={selectedId} onChange={(e) => setSelectedId(e.target.value)}>
                <option value="">-- Select from inventory --</option>
                {foods.map((f) => (
                  <option key={f._id} value={f._id}>
                    {f.label} – {f.predictedExpiryDate || "no expiry yet"}
                  </option>
                ))}
              </select>
              {errors.foodId && <span className="fe-form__error">{errors.foodId}</span>}
            </div>

            <div className="fe-form__grid">
              <div className="fe-form__group">
                <label>User ID</label>
                <input type="text" name="userId" value={form.userId} onChange={handleChange} />
                {errors.userId && <span className="fe-form__error">{errors.userId}</span>}
                <div className="fe-muted fe-small">
                  Must match the User ID used when adding/predicting items (stored in FE_DEMO_USER_ID).
                </div>
              </div>

              <div className="fe-form__group">
                <label>Feedback Type</label>
                <select name="feedback" value={form.feedback} onChange={handleChange}>
                  <option value="early">Spoiled earlier than predicted</option>
                  <option value="on_time">Prediction was correct</option>
                  <option value="late">Stayed fresh longer than predicted</option>
                </select>
              </div>
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
              {errors.actual_days && <span className="fe-form__error">{errors.actual_days}</span>}
            </div>

            {selectedFood && (
              <div className="fe-result-box mt-3">
                <div className="fe-small fe-muted">Selected item</div>
                <div className="fe-strong">{selectedFood.label}</div>
                <div className="fe-muted fe-small">
                  Item key: <strong>{selectedFood.item_name || "—"}</strong>
                </div>
              </div>
            )}

            {apiError && <div className="fe-alert fe-alert--error mt-3">{apiError}</div>}
            {success && <div className="fe-alert fe-alert--success mt-3">{success}</div>}

            <button className="fe-btn fe-btn--primary mt-4" type="submit">
              Submit Feedback
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
