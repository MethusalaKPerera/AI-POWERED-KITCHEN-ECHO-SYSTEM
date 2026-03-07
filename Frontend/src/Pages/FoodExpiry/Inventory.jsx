// src/Pages/FoodExpiry/Inventory.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { getAllFoods, deleteFood, updateFood, predictExpiry } from "../../api/foodApi.js";
import "./foodexpiry.css";

/* -----------------------------
   Sri Lanka region → typical humidity mapping (simple demo-friendly)
   (You can tune these later; panel-friendly: we show "region based humidity")
----------------------------- */
const SL_REGIONS = [
  { key: "Western", humidity: 78 },
  { key: "Central", humidity: 72 },
  { key: "Southern", humidity: 80 },
  { key: "Northern", humidity: 70 },
  { key: "Eastern", humidity: 75 },
  { key: "North Western", humidity: 76 },
  { key: "North Central", humidity: 68 },
  { key: "Uva", humidity: 74 },
  { key: "Sabaragamuwa", humidity: 79 },
];

function regionToHumidity(regionKey) {
  const r = SL_REGIONS.find((x) => x.key === regionKey);
  return r ? r.humidity : 78;
}

// ✅ NEW (necessary): DB/backend stores region in lowercase sometimes (e.g., "western")
// This maps it back to the exact dropdown key.
function normalizeRegionKey(regionVal) {
  const raw = String(regionVal || "").trim();
  if (!raw) return "Western";
  const found = SL_REGIONS.find((r) => r.key.toLowerCase() === raw.toLowerCase());
  return found ? found.key : "Western";
}

function defaultTempByStorage(storage) {
  const s = String(storage || "pantry").toLowerCase();
  if (s === "freezer") return -18;
  if (s === "fridge") return 4;
  return 28;
}

function clamp(num, min, max) {
  const n = Number(num);
  if (Number.isNaN(n)) return min;
  return Math.min(max, Math.max(min, n));
}

/* -----------------------------
   Helpers
----------------------------- */
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

    predictedExpiryDate:
      f.finalExpiryDate || f.predictedExpiryDate || f.predicted_expiry_date || "",

    scpPriorityScore:
      f.scpPriorityScore_live ?? f.scpPriorityScore ?? f.scp_priority_score ?? null,

    printedExpiryDate: f.printedExpiryDate || "",

    // optional if backend stores
    region: f.region || "",
    storage_temperature_c: f.storage_temperature_c ?? null,
    storage_humidity_pct: f.storage_humidity_pct ?? null,
  };
}

function scpLabel(score) {
  if (score === null || score === undefined) return "—";
  const s = Number(score);
  if (Number.isNaN(s)) return "—";
  if (s >= 0.9) return "High";
  if (s >= 0.6) return "Medium";
  return "Low";
}

function isFuturePurchase(purchase_date) {
  if (!purchase_date) return false;
  const p = new Date(purchase_date + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return p.getTime() > today.getTime();
}

function daysUntilPurchase(purchase_date) {
  if (!purchase_date) return null;
  const p = new Date(purchase_date + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.round((p.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

function addDaysToDate(dateStr, days) {
  if (!dateStr || days === null || days === undefined) return null;
  const d = new Date(dateStr + "T00:00:00");
  if (Number.isNaN(d.getTime())) return null;
  d.setDate(d.getDate() + Math.round(Number(days)));
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function daysBetween(fromDateStr, toDateStr) {
  if (!fromDateStr || !toDateStr) return null;
  const a = new Date(fromDateStr + "T00:00:00");
  const b = new Date(toDateStr + "T00:00:00");
  if (Number.isNaN(a.getTime()) || Number.isNaN(b.getTime())) return null;
  return Math.round((b.getTime() - a.getTime()) / (1000 * 60 * 60 * 24));
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

/* -----------------------------
   Component
----------------------------- */
export default function Inventory() {
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");

  // Edit modal
  const [editItem, setEditItem] = useState(null);
  const [editError, setEditError] = useState("");
  const [saving, setSaving] = useState(false);

  // Predict modal
  const [predictItem, setPredictItem] = useState(null);
  const [predictPrinted, setPredictPrinted] = useState("");
  const [noPrinted, setNoPrinted] = useState(false);
  const [predictLoading, setPredictLoading] = useState(false);
  const [predictError, setPredictError] = useState("");
  const [predictResult, setPredictResult] = useState(null);

  // ✅ Environment fields (user enters during prediction)
  const [predictRegion, setPredictRegion] = useState("Western");
  const [predictHumidity, setPredictHumidity] = useState(regionToHumidity("Western"));
  const [predictTemp, setPredictTemp] = useState(28);

  const navigate = useNavigate();

  async function load() {
    try {
      setLoading(true);
      const data = await getAllFoods();
      const rows = (Array.isArray(data) ? data : []).map(normalizeFood);
      setFoods(rows);
      return rows;
    } catch (err) {
      setApiError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  // ✅ lock background scroll when modal is open
  useEffect(() => {
    const open = Boolean(predictItem || editItem);
    if (open) document.body.classList.add("fe-modal-open");
    else document.body.classList.remove("fe-modal-open");

    return () => document.body.classList.remove("fe-modal-open");
  }, [predictItem, editItem]);

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

  // -------------------------
  // EDIT
  // -------------------------
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

      const payload = {
        foodName: editItem.foodName,
        item_name: editItem.item_name,
        item_category: editItem.item_category,
        storage_type: editItem.storage_type,
        purchase_date: editItem.purchase_date,
        quantity: Number(editItem.quantity || 1),
        used_before_expiry: Boolean(editItem.used_before_expiry),
        // ✅ backend update route accepts printedExpiryDate
        printedExpiryDate: editItem.printedExpiryDate || "",
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

  // -------------------------
  // PREDICT
  // -------------------------
  function startPredict(item) {
    setPredictItem({ ...item });
    setPredictResult(null);
    setPredictError("");

    const existingPrinted = item.printedExpiryDate || "";
    setPredictPrinted(existingPrinted);
    setNoPrinted(!existingPrinted);

    // ✅ set smart defaults for env (based on storage + region)
    const storage = item.storage_type || "pantry";

    // ✅ use normalized region key (handles backend-stored lowercase)
    const prevRegion = normalizeRegionKey(item.region || "Western");

    const prevHum =
      item.storage_humidity_pct !== null && item.storage_humidity_pct !== undefined
        ? Number(item.storage_humidity_pct)
        : regionToHumidity(prevRegion);

    const prevTemp =
      item.storage_temperature_c !== null && item.storage_temperature_c !== undefined
        ? Number(item.storage_temperature_c)
        : defaultTempByStorage(storage);

    setPredictRegion(prevRegion);
    setPredictHumidity(clamp(prevHum, 30, 98));
    setPredictTemp(
      clamp(
        prevTemp,
        storage === "freezer" ? -30 : 0,
        storage === "freezer" ? 0 : 40
      )
    );
  }

  function closePredict() {
    setPredictItem(null);
    setPredictResult(null);
    setPredictError("");
    setPredictLoading(false);
    setPredictPrinted("");
    setNoPrinted(false);
  }

  // when region changes -> auto update humidity to match region (user can still manually adjust)
  function handleRegionChange(val) {
    setPredictRegion(val);
    setPredictHumidity(regionToHumidity(val));
  }

  async function runPredict() {
    if (!predictItem) return;

    if (!predictItem.userId) {
      setPredictError("User ID missing for this item.");
      return;
    }
    if (!predictItem.item_name || !predictItem.item_category || !predictItem.purchase_date) {
      setPredictError("Missing item_name / category / purchase_date. Please edit the item first.");
      return;
    }

    // ✅ Validate environment (UI-level)
    const storage = String(predictItem.storage_type || "pantry").toLowerCase();
    const hum = clamp(predictHumidity, 30, 98);

    // storage-specific reasonable temp ranges (panel-friendly)
    let tempMin = 0;
    let tempMax = 40;
    if (storage === "fridge") {
      tempMin = 0;
      tempMax = 10;
    } else if (storage === "freezer") {
      tempMin = -30;
      tempMax = 0;
    } else {
      tempMin = 10;
      tempMax = 40;
    }
    const temp = clamp(predictTemp, tempMin, tempMax);

    try {
      setPredictLoading(true);
      setPredictError("");
      setPredictResult(null);

      const payload = {
        foodId: predictItem._id,
        userId: predictItem.userId,
        item_name: predictItem.item_name,
        item_category: predictItem.item_category,
        purchase_date: predictItem.purchase_date,
        quantity: Number(predictItem.quantity || 1),
        storage_type: predictItem.storage_type,
        used_before_expiry: Boolean(predictItem.used_before_expiry),

        printed_expiry_date: noPrinted ? null : predictPrinted || null,

        // ✅ environment passed from UI at prediction time
        region: predictRegion,
        storage_temperature_c: temp,
        storage_humidity_pct: hum,
      };

      const data = await predictExpiry(payload);
      setPredictResult(data);

      // refresh inventory so finalExpiry/SCP persists
      const rows = await load();
      const updated = rows.find((r) => r._id === predictItem._id);
      if (updated) {
        setPredictItem(updated);

        // ✅ NEW (necessary): refresh env fields from DB after predict save (better UX)
        const dbRegion = normalizeRegionKey(updated.region || predictRegion);
        setPredictRegion(dbRegion);

        if (updated.storage_humidity_pct !== null && updated.storage_humidity_pct !== undefined) {
          setPredictHumidity(Number(updated.storage_humidity_pct));
        }

        if (updated.storage_temperature_c !== null && updated.storage_temperature_c !== undefined) {
          setPredictTemp(Number(updated.storage_temperature_c));
        }
      }
    } catch (err) {
      setPredictError(err.message);
    } finally {
      setPredictLoading(false);
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
                  <th>User ID</th>
                  <th>Category</th>
                  <th>Storage</th>
                  <th>Purchase</th>
                  <th>Final Expiry</th>
                  <th>Qty</th>
                  <th>SCP</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {loading && (
                  <tr>
                    <td colSpan={9}>Loading...</td>
                  </tr>
                )}

                {!loading &&
                  sortedFoods.map((f) => (
                    <tr key={f._id}>
                      <td>
                        <div className="fe-strong">{f.foodName || f.item_name}</div>
                        <div className="fe-muted fe-small">{f.item_name}</div>
                      </td>

                      <td>
                        <span className="fe-muted">{f.userId || "—"}</span>
                      </td>

                      <td>{f.item_category}</td>
                      <td>{f.storage_type}</td>
                      <td>{f.purchase_date || "—"}</td>
                      <td>{f.predictedExpiryDate || "—"}</td>
                      <td>{f.quantity ?? "-"}</td>

                      <td>
                        {isFuturePurchase(f.purchase_date) ? (
                          <span className="fe-muted">
                            — (Not started
                            {daysUntilPurchase(f.purchase_date) !== null
                              ? `, in ${daysUntilPurchase(f.purchase_date)} day(s)`
                              : ""}
                            )
                          </span>
                        ) : (
                          <>
                            {f.scpPriorityScore ?? "—"}
                            {f.scpPriorityScore !== null && f.scpPriorityScore !== undefined && (
                              <span className="fe-muted fe-small"> ({scpLabel(f.scpPriorityScore)})</span>
                            )}
                          </>
                        )}
                      </td>

                      <td className="fe-actions">
                        <button
                          className="fe-btn fe-btn--primary"
                          onClick={() => startPredict(f)}
                          disabled={isFuturePurchase(f.purchase_date)}
                          title={
                            isFuturePurchase(f.purchase_date)
                              ? "Prediction activates after purchase date"
                              : ""
                          }
                        >
                          Predict
                        </button>

                        <button className="fe-btn fe-btn--ghost" onClick={() => startEdit(f)}>
                          Edit
                        </button>

                        <button className="fe-btn fe-btn--danger" onClick={() => handleDelete(f._id)}>
                          Delete
                        </button>

                        <button
                          className="fe-btn fe-btn--ghost"
                          onClick={() => navigate(`/food-expiry/predict?foodId=${f._id}`)}
                        >
                          History
                        </button>
                      </td>
                    </tr>
                  ))}

                {!loading && sortedFoods.length === 0 && (
                  <tr>
                    <td colSpan={9}>No data yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* ----------------------------- */}
          {/* PREDICT MODAL */}
          {/* ----------------------------- */}
          {predictItem && (
            <div className="fe-modal" role="dialog" aria-modal="true">
              <div className="fe-modal__content">
                <div className="fe-modal__header">
                  <h3 style={{ margin: 0 }}>Predict Expiry</h3>
                  <button className="fe-btn fe-btn--ghost" onClick={closePredict}>
                    ✕
                  </button>
                </div>

                <div className="fe-result-box">
                  <div className="fe-small fe-muted">Stored item details (read-only)</div>
                  <div className="fe-strong">{predictItem.foodName || predictItem.item_name}</div>
                  <div className="fe-muted fe-small">User ID: {predictItem.userId || "—"}</div>
                  <div className="fe-muted fe-small">
                    Item: {predictItem.item_name} • Category: {predictItem.item_category}
                  </div>
                  <div className="fe-muted fe-small">
                    Purchase: {predictItem.purchase_date} • Storage: {predictItem.storage_type} • Qty:{" "}
                    {predictItem.quantity ?? 1}
                  </div>
                </div>

                {/* ✅ ENVIRONMENT INPUTS */}
                <div className="fe-card mt-3">
                  <h4 className="fe-section__title mb-2" style={{ fontSize: 16 }}>
                    Storage Environment (for prediction)
                  </h4>
                  <div className="fe-muted fe-small" style={{ marginBottom: 10 }}>
                    Select your region to apply a typical humidity value for Sri Lanka, and enter the storage temperature.
                    <br />
                    <span className="fe-muted fe-small">
                      Note: The backend may clamp values to storage-safe bounds for consistency with the trained model.
                    </span>
                  </div>

                  <div className="fe-form__grid">
                    <div className="fe-form__group">
                      <label>Region (Sri Lanka)</label>
                      <select value={predictRegion} onChange={(e) => handleRegionChange(e.target.value)}>
                        {SL_REGIONS.map((r) => (
                          <option key={r.key} value={r.key}>
                            {r.key} (≈ {r.humidity}% humidity)
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="fe-form__group">
                      <label>Humidity (%)</label>
                      <input
                        type="number"
                        min="30"
                        max="98"
                        value={predictHumidity}
                        onChange={(e) => setPredictHumidity(e.target.value)}
                      />
                      <div className="fe-muted fe-small">Auto-filled from region, but you can adjust.</div>
                    </div>
                  </div>

                  <div className="fe-form__group mt-2">
                    <label>Temperature (°C)</label>
                    <input
                      type="number"
                      value={predictTemp}
                      onChange={(e) => setPredictTemp(e.target.value)}
                    />
                    <div className="fe-muted fe-small">
                      Defaults: Pantry ≈ 28°C • Fridge ≈ 4°C • Freezer ≈ -18°C
                    </div>
                  </div>
                </div>

                <div className="fe-form__group mt-3">
                  <label>Printed Expiry Date (optional)</label>
                  <input
                    type="date"
                    value={predictPrinted || ""}
                    onChange={(e) => setPredictPrinted(e.target.value)}
                    disabled={noPrinted}
                  />
                </div>

                <div className="fe-form__group fe-form__group--inline">
                  <label>
                    <input
                      type="checkbox"
                      checked={noPrinted}
                      onChange={(e) => {
                        const v = e.target.checked;
                        setNoPrinted(v);
                        if (v) setPredictPrinted("");
                      }}
                    />
                    &nbsp; No printed expiry available
                  </label>
                </div>

                {predictError && <div className="fe-alert fe-alert--error mt-3">{predictError}</div>}

                <div className="fe-modal__actions">
                  <button className="fe-btn fe-btn--ghost" onClick={closePredict} disabled={predictLoading}>
                    Close
                  </button>
                  <button className="fe-btn fe-btn--primary" onClick={runPredict} disabled={predictLoading}>
                    {predictLoading ? "Predicting..." : "Run Prediction"}
                  </button>
                </div>

                {predictResult && (
                  <div className="fe-card mt-4">
                    <h4 className="fe-section__title mb-3">Prediction Result</h4>

                    {(() => {
                      const purchaseDate = predictItem?.purchase_date || null;
                      const baselineDays = predictResult.baseline_days ?? null;
                      const personalizedDays = predictResult.personalized_days ?? null;

                      const baselineExpiry =
                        predictResult.baseline_expiry_date ||
                        (purchaseDate ? addDaysToDate(purchaseDate, baselineDays) : null);

                      const personalizedExpiryBeforeSafety =
                        predictResult.personalized_expiry_date ||
                        (purchaseDate && predictResult.personalization_enabled
                          ? addDaysToDate(purchaseDate, personalizedDays)
                          : null);

                      const finalExpiry = predictResult.final_expiry_date || null;

                      const daysLeftFromBaseline = baselineExpiry
                        ? daysBetween(todayISO(), baselineExpiry)
                        : null;

                      const daysLeftFromPersonal = personalizedExpiryBeforeSafety
                        ? daysBetween(todayISO(), personalizedExpiryBeforeSafety)
                        : null;

                      // ✅ NEW (necessary): show actual env values used by backend (clamped), not just local input
                      const usedRegion = predictResult.region || predictRegion;
                      const usedTemp =
                        predictResult.storage_temperature_c !== null &&
                        predictResult.storage_temperature_c !== undefined
                          ? predictResult.storage_temperature_c
                          : predictTemp;

                      const usedHum =
                        predictResult.storage_humidity_pct !== null &&
                        predictResult.storage_humidity_pct !== undefined
                          ? predictResult.storage_humidity_pct
                          : predictHumidity;

                      return (
                        <div className="fe-result-box">
                          <p className="fe-muted fe-small" style={{ marginBottom: 6 }}>
                            Environment used:
                          </p>
                          <p className="fe-muted fe-small" style={{ marginTop: 0 }}>
                            Region: <strong>{String(usedRegion || "—")}</strong> • Temp:{" "}
                            <strong>{clamp(usedTemp, -30, 60)}°C</strong> • Humidity:{" "}
                            <strong>{clamp(usedHum, 0, 100)}%</strong>
                          </p>

                          <div style={{ height: 10 }} />

                          <p className="fe-muted fe-small" style={{ marginBottom: 6 }}>
                            Baseline (Original) Expiry Date:
                          </p>
                          <p style={{ fontWeight: 700, marginTop: 0 }}>{baselineExpiry || "—"}</p>

                          {predictResult.personalization_enabled && (
                            <>
                              <div style={{ height: 10 }} />
                              <p className="fe-muted fe-small" style={{ marginBottom: 6 }}>
                                Personalized Expiry (Before Safety):
                              </p>
                              <p style={{ fontWeight: 700, marginTop: 0 }}>
                                {personalizedExpiryBeforeSafety || "—"}{" "}
                                <span className="fe-muted fe-small">← derived from your habits</span>
                              </p>
                            </>
                          )}

                          <div style={{ height: 10 }} />
                          <p className="fe-muted fe-small" style={{ marginBottom: 6 }}>
                            Final Expiry Date (Used by System):
                          </p>
                          <p
                            style={{
                              fontWeight: 900,
                              marginTop: 0,
                              padding: "10px 12px",
                              borderRadius: 10,
                              background: "rgba(34,197,94,0.10)",
                              display: "inline-block",
                            }}
                          >
                            {finalExpiry || "—"}
                          </p>

                          <div style={{ height: 10 }} />
                          <p className="fe-muted fe-small">
                            Days left from original expiry:{" "}
                            <strong>{daysLeftFromBaseline !== null ? daysLeftFromBaseline : "—"}</strong>
                          </p>

                          {predictResult.personalization_enabled && (
                            <p className="fe-muted fe-small">
                              Days left from personalized expiry:{" "}
                              <strong>{daysLeftFromPersonal !== null ? daysLeftFromPersonal : "—"}</strong>
                            </p>
                          )}

                          <p className="mt-2">
                            <strong>SCP Priority Score:</strong>{" "}
                            {predictResult.scpPriorityScore ?? "—"}{" "}
                            {predictResult.scpPriorityScore !== null &&
                              predictResult.scpPriorityScore !== undefined && (
                                <span className="fe-muted fe-small">
                                  ({scpLabel(predictResult.scpPriorityScore)})
                                </span>
                              )}
                          </p>
                        </div>
                      );
                    })()}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ----------------------------- */}
          {/* EDIT MODAL */}
          {/* ----------------------------- */}
          {editItem && (
            <div className="fe-modal" role="dialog" aria-modal="true">
              <div className="fe-modal__content">
                <div className="fe-modal__header">
                  <h3 style={{ margin: 0 }}>Edit Item</h3>
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
                    <input
                      name="item_category"
                      value={editItem.item_category || ""}
                      onChange={handleEditChange}
                    />
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
                    <input
                      type="date"
                      name="purchase_date"
                      value={editItem.purchase_date || ""}
                      onChange={handleEditChange}
                    />
                  </div>
                </div>

                <div className="fe-form__grid">
                  <div className="fe-form__group">
                    <label>Quantity</label>
                    <input
                      type="number"
                      name="quantity"
                      min="1"
                      value={editItem.quantity ?? 1}
                      onChange={handleEditChange}
                    />
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

                <div className="fe-form__group">
                  <label>Printed Expiry Date (optional)</label>
                  <input
                    type="date"
                    name="printedExpiryDate"
                    value={editItem.printedExpiryDate || ""}
                    onChange={handleEditChange}
                  />
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