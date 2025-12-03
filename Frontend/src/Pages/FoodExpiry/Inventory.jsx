// src/Pages/FoodExpiry/Inventory.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import {
  getAllFoods,
  deleteFood,
  updateFood,
} from "../../api/foodApi.js";
import "./foodExpiry.css";

export default function Inventory() {
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");
  const [editItem, setEditItem] = useState(null);
  const [editError, setEditError] = useState("");

  async function load() {
    try {
      setLoading(true);
      const data = await getAllFoods();
      setFoods(data || []);
    } catch (err) {
      setApiError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleDelete(id) {
    if (!window.confirm("Delete this item?")) return;
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
    const { name, value } = e.target;
    setEditItem((prev) => ({ ...prev, [name]: value }));
  }

  async function saveEdit() {
    if (!editItem) return;
    if (!editItem.foodName || !editItem.purchaseDate) {
      setEditError("Food name and purchase date are required");
      return;
    }

    try {
      const payload = {
        foodName: editItem.foodName,
        itemName: editItem.itemName,
        category: editItem.category,
        storageType: editItem.storageType,
        purchaseDate: editItem.purchaseDate,
        quantity: editItem.quantity,
        used_before_exp: editItem.used_before_exp,
      };
      await updateFood(editItem._id, payload);
      setEditItem(null);
      load();
    } catch (err) {
      setEditError(err.message);
    }
  }

  return (
    <div className="fe-layout">
      <Sidebar />
      <div className="fe-main">
        <Topbar title="Inventory" />
        <div className="fe-main__content">
          {apiError && <div className="fe-alert fe-alert--error">{apiError}</div>}

          <div className="fe-table-wrapper">
            <table className="fe-table">
              <thead>
                <tr>
                  <th>Food</th>
                  <th>Category</th>
                  <th>Storage</th>
                  <th>Purchase</th>
                  <th>Expiry</th>
                  <th>Qty</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr>
                    <td colSpan={7}>Loading...</td>
                  </tr>
                )}
                {!loading &&
                  foods.map((f) => (
                    <tr key={f._id}>
                      <td>{f.foodName || f.itemName}</td>
                      <td>{f.category}</td>
                      <td>{f.storageType}</td>
                      <td>{f.purchaseDate}</td>
                      <td>{f.predictedExpiryDate || "—"}</td>
                      <td>{f.quantity ?? "-"}</td>
                      <td>
                        <button
                          className="fe-btn fe-btn--ghost"
                          onClick={() => startEdit(f)}
                        >
                          Edit
                        </button>
                        <button
                          className="fe-btn fe-btn--danger ml-2"
                          onClick={() => handleDelete(f._id)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                {!loading && foods.length === 0 && (
                  <tr>
                    <td colSpan={7}>No data yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Edit modal */}
          {editItem && (
            <div className="fe-modal">
              <div className="fe-modal__content">
                <h3>Edit Food</h3>
                <div className="fe-form__group">
                  <label>Food Name</label>
                  <input
                    name="foodName"
                    value={editItem.foodName || ""}
                    onChange={handleEditChange}
                  />
                </div>
                <div className="fe-form__group">
                  <label>Category</label>
                  <input
                    name="category"
                    value={editItem.category || ""}
                    onChange={handleEditChange}
                  />
                </div>
                <div className="fe-form__group">
                  <label>Storage Type</label>
                  <input
                    name="storageType"
                    value={editItem.storageType || ""}
                    onChange={handleEditChange}
                  />
                </div>
                <div className="fe-form__group">
                  <label>Purchase Date</label>
                  <input
                    name="purchaseDate"
                    value={editItem.purchaseDate || ""}
                    onChange={handleEditChange}
                  />
                </div>
                <div className="fe-form__group">
                  <label>Quantity</label>
                  <input
                    name="quantity"
                    type="number"
                    value={editItem.quantity ?? ""}
                    onChange={handleEditChange}
                  />
                </div>

                {editError && (
                  <div className="fe-alert fe-alert--error">{editError}</div>
                )}

                <div className="fe-modal__actions">
                  <button className="fe-btn fe-btn--ghost" onClick={() => setEditItem(null)}>
                    Cancel
                  </button>
                  <button className="fe-btn fe-btn--primary" onClick={saveEdit}>
                    Save
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
