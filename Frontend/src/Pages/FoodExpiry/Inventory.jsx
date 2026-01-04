import React, { useEffect, useMemo, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { getAllFoods, deleteFood, updateFood } from "../../api/foodApi.js";
import "./foodexpiry.css";

function normalizeFood(f) {
  return {
    _id: f._id,
    userId: f.userId || f.user_id || "",
    foodName: f.foodName || f.food_name || "",
    item_name: f.itemName || f.item_name || "",
    item_category: f.category || f.item_category || "",
    storage_type: f.storageType || f.storage_type || "pantry",
    purchase_date: f.purchaseDate || f.purchase_date || "",
    quantity: f.quantity ?? 1,
    used_before_expiry: Boolean(f.used_before_expiry ?? f.used_before_exp ?? false),
    predictedExpiryDate: f.predictedExpiryDate || f.predicted_expiry_date || "",
    scpPriorityScore: f.scpPriorityScore ?? f.scp_priority_score ?? null,
  };
}

export default function Inventory() {
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");

  const [editItem, setEditItem] = useState(null);
  const [editError, setEditError] = useState("");
  const [saving, setSaving] = useState(false);

  async function load() {
    try {
      setLoading(true);
      const data = await getAllFoods();
      const rows = (Array.isArray(data) ? data : []).map(normalizeFood);
      setFoods(rows);
    } catch (err) {
      setApiError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const sortedFoods = useMemo(() => {
    return [...foods].sort((a, b) => {
      const da = new Date(a.predictedExpiryDate || "2100-01-01").getTime();
      const db = new Date(b.predictedExpiryDate || "2100-01-01").getTime();
      return da - db;
    });
  }, [foods]);

  async function handleDelete(id) {
    if (!window.confirm("Delete this item from inventory?")) return;
    try {
      await deleteFood(id);
      setFoods((prev) => prev.filter((f) => f._id !== id));
    } catch (err) {
      alert(err.message);
    }
  }

  function startEdit(item) {
    setEditItem({ ...item });
    setEditError("");
  }

  function handleEditChange(e) {
    const { name, value, type, checked } = e.target;
    setEditItem((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  async function saveEdit() {
    if (!editItem) return;

    if (!editItem.foodName?.trim()) {
      setEditError("Food name is required.");
      return;
    }
    if (!editItem.purchase_date) {
      setEditError("Purchase date is required.");
      return;
    }

    try {
      setSaving(true);

      // ✅ Send payload aligned with backend (snake_case)
      const payload = {
        foodName: editItem.foodName,
        item_name: editItem.item_name,
        item_category: editItem.item_category,
        storage_type: editItem.storage_type,
        purchase_date: editItem.purchase_date,
        quantity: Number(editItem.quantity || 1),
        used_before_expiry: Boolean(editItem.used_before_expiry),
      };

      await updateFood(editItem._id, payload);
      setEditItem(null);
      await load();
    } catch (err) {
      setEditError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fe-layout">
      <Sidebar />
      <div className="fe-main">
        <Topbar title="Inventory" />
        <div className="fe-main__content">
          {apiError && <div className="fe-alert fe-alert--error">{apiError}</div>}

          <div className="fe-table-wrapper fe-card">
            <div className="fe-table-header">
              <h2 className="fe-section__title">Stored Items</h2>
              <span className="fe-muted">{sortedFoods.length} items</span>
            </div>

            <table className="fe-table">
              <thead>
                <tr>
                  <th>Food</th>
                  <th>Category</th>
                  <th>Storage</th>
                  <th>Purchase</th>
                  <th>Predicted Expiry</th>
                  <th>Qty</th>
                  <th>SCP</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr>
                    <td colSpan={8}>Loading...</td>
                  </tr>
                )}

                {!loading &&
                  sortedFoods.map((f) => (
                    <tr key={f._id}>
                      <td>
                        <div className="fe-strong">{f.foodName || f.item_name}</div>
                        <div className="fe-muted fe-small">{f.item_name}</div>
                      </td>
                      <td>{f.item_category}</td>
                      <td>{f.storage_type}</td>
                      <td>{f.purchase_date || "—"}</td>
                      <td>{f.predictedExpiryDate || "—"}</td>
                      <td>{f.quantity ?? "-"}</td>
                      <td>{f.scpPriorityScore ?? "—"}</td>
                      <td className="fe-actions">
                        <button className="fe-btn fe-btn--ghost" onClick={() => startEdit(f)}>
                          Edit
                        </button>
                        <button className="fe-btn fe-btn--danger" onClick={() => handleDelete(f._id)}>
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}

                {!loading && sortedFoods.length === 0 && (
                  <tr>
                    <td colSpan={8}>No data yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Edit modal */}
          {editItem && (
            <div className="fe-modal">
              <div className="fe-modal__content">
                <div className="fe-modal__header">
                  <h3>Edit Item</h3>
                  <button className="fe-btn fe-btn--ghost" onClick={() => setEditItem(null)}>
                    ✕
                  </button>
                </div>

                <div className="fe-form__group">
                  <label>Food Name</label>
                  <input name="foodName" value={editItem.foodName || ""} onChange={handleEditChange} />
                </div>

                <div className="fe-form__grid">
                  <div className="fe-form__group">
                    <label>Item Name</label>
                    <input name="item_name" value={editItem.item_name || ""} onChange={handleEditChange} />
                  </div>
                  <div className="fe-form__group">
                    <label>Category</label>
                    <input name="item_category" value={editItem.item_category || ""} onChange={handleEditChange} />
                  </div>
                </div>

                <div className="fe-form__grid">
                  <div className="fe-form__group">
                    <label>Storage</label>
                    <select name="storage_type" value={editItem.storage_type} onChange={handleEditChange}>
                      <option value="fridge">Fridge</option>
                      <option value="freezer">Freezer</option>
                      <option value="pantry">Pantry</option>
                    </select>
                  </div>
                  <div className="fe-form__group">
                    <label>Purchase Date</label>
                    <input type="date" name="purchase_date" value={editItem.purchase_date || ""} onChange={handleEditChange} />
                  </div>
                </div>

                <div className="fe-form__grid">
                  <div className="fe-form__group">
                    <label>Quantity</label>
                    <input type="number" name="quantity" min="1" value={editItem.quantity ?? 1} onChange={handleEditChange} />
                  </div>

                  <div className="fe-form__group fe-form__group--inline">
                    <label>
                      <input
                        type="checkbox"
                        name="used_before_expiry"
                        checked={!!editItem.used_before_expiry}
                        onChange={handleEditChange}
                      />
                      &nbsp; Usually used before expiry
                    </label>
                  </div>
                </div>

                {editError && <div className="fe-alert fe-alert--error">{editError}</div>}

                <div className="fe-modal__actions">
                  <button className="fe-btn fe-btn--ghost" onClick={() => setEditItem(null)}>
                    Cancel
                  </button>
                  <button className="fe-btn fe-btn--primary" onClick={saveEdit} disabled={saving}>
                    {saving ? "Saving..." : "Save Changes"}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
