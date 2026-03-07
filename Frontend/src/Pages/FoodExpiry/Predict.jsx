import React, { useEffect, useMemo, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { getAllFoods } from "../../api/foodApi.js";
import "./foodexpiry.css";

/**
 * This page is a READ-ONLY dashboard for PP1/PP2:
 * - Shows prediction history saved in MongoDB (predictionHistory)
 * - Shows baseline vs personalized vs final expiry
 * - Shows SCP priority list
 * - (PP2 ready) shows environment values used (region / temp / humidity) if backend stores them
 */

function normalizeFood(f) {
  return {
    _id: f._id,
    userId: f.userId || "",
    foodName: f.foodName || "",
    itemName: f.itemName || "",
    category: f.category || "",
    storageType: f.storageType || "pantry",
    purchaseDate: f.purchaseDate || "",
    printedExpiryDate: f.printedExpiryDate || "",

    baselineExpiryDate: f.baselineExpiryDate || "",
    personalizedExpiryDate: f.personalizedExpiryDate || "",
    finalExpiryDate: f.finalExpiryDate || f.predictedExpiryDate || "",

    scpPriorityScore: f.scpPriorityScore ?? null,
    daysLeftAtSave: f.daysLeftAtSave ?? null,

    // ✅ PP2: store last-used environment at food level (if backend saved)
    region: f.region || "",
    storage_temperature_c: f.storage_temperature_c ?? null,
    storage_humidity_pct: f.storage_humidity_pct ?? null,

    predictionHistory: Array.isArray(f.predictionHistory) ? f.predictionHistory : [],
  };
}

function fmtDate(d) {
  if (!d) return "—";
  return d;
}

function fmtNum(n) {
  if (n === null || n === undefined) return "—";
  const v = Number(n);
  if (Number.isNaN(v)) return "—";
  return v.toFixed(2);
}

function scpLabel(score) {
  if (score === null || score === undefined) return "—";
  const s = Number(score);
  if (Number.isNaN(s)) return "—";
  if (s >= 0.9) return "High";
  if (s >= 0.6) return "Medium";
  return "Low";
}

function safeText(v) {
  return v === null || v === undefined || String(v).trim() === "" ? "—" : String(v);
}

export default function Predict() {
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");

  // For PP1/PP2 demo, view one user at a time
  const [userId, setUserId] = useState("demo"); // ✅ set to your real default userId in DB (e.g., U001 / demo)
  const [selectedFoodId, setSelectedFoodId] = useState("");

  async function load() {
    try {
      setLoading(true);
      setApiError("");
      const data = await getAllFoods();
      const rows = (Array.isArray(data) ? data : []).map(normalizeFood);
      setFoods(rows);

      // Helpful for debugging: see available userIds in console
      // (You can remove this later)
      const ids = Array.from(new Set(rows.map((r) => r.userId).filter(Boolean)));
      // eslint-disable-next-line no-console
      console.log("Available userIds in foods:", ids);
    } catch (err) {
      setApiError(err?.message || "Failed to load foods");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  // filter by user (exact match)
  const userFoods = useMemo(() => {
    return foods.filter((f) => (f.userId || "") === (userId || ""));
  }, [foods, userId]);

  // auto-select first item if nothing selected
  useEffect(() => {
    if (!selectedFoodId && userFoods.length > 0) {
      setSelectedFoodId(userFoods[0]._id);
    }
  }, [userFoods, selectedFoodId]);

  const selectedFood = useMemo(() => {
    return userFoods.find((f) => f._id === selectedFoodId) || null;
  }, [userFoods, selectedFoodId]);

  // History sorted newest first
  const history = useMemo(() => {
    if (!selectedFood) return [];
    const h = selectedFood.predictionHistory || [];
    return [...h].sort((a, b) => {
      const ta = new Date(a.ts || 0).getTime();
      const tb = new Date(b.ts || 0).getTime();
      return tb - ta;
    });
  }, [selectedFood]);

  // Top priority list: SCP desc, daysLeft asc
  const priorityList = useMemo(() => {
    const rows = [...userFoods];
    rows.sort((a, b) => {
      const sa = a.scpPriorityScore ?? -999;
      const sb = b.scpPriorityScore ?? -999;
      if (sb !== sa) return sb - sa;

      const da = a.daysLeftAtSave ?? 9999;
      const db = b.daysLeftAtSave ?? 9999;
      return da - db;
    });
    return rows.slice(0, 10);
  }, [userFoods]);

  // Show hint if user typed a userId that doesn't exist
  const availableUserIds = useMemo(() => {
    return Array.from(new Set(foods.map((f) => f.userId).filter(Boolean))).sort();
  }, [foods]);

  const showUserHint = useMemo(() => {
    if (!userId) return false;
    if (loading) return false;
    if (foods.length === 0) return false;
    // If there are foods but none match the typed userId, show hint
    return userFoods.length === 0 && availableUserIds.length > 0;
  }, [userId, loading, foods.length, userFoods.length, availableUserIds.length]);

  return (
    <div className="fe-layout">
      <Sidebar />
      <div className="fe-main">
        <Topbar title="Prediction History" />
        <div className="fe-main__content">
          {apiError && <div className="fe-alert fe-alert--error">{apiError}</div>}

          <div className="fe-card fe-form fe-form--wide">
            <div className="fe-table-header">
              <h2 className="fe-section__title">History of Predictions</h2>
              <button className="fe-btn fe-btn--ghost" onClick={load} disabled={loading}>
                {loading ? "Refreshing..." : "Refresh"}
              </button>
            </div>

            <div className="fe-form__grid">
              <div className="fe-form__group">
                <label>User ID (view one user)</label>
                <input
                  type="text"
                  value={userId}
                  onChange={(e) => {
                    setUserId(e.target.value);
                    setSelectedFoodId("");
                  }}
                  placeholder="E.g. U001"
                />
                <div className="fe-muted fe-small">
                  Type the exact <b>userId</b> stored in MongoDB (e.g., <b>U001</b>, <b>U002</b>, <b>demo</b>).
                </div>

                {showUserHint && (
                  <div className="fe-alert fe-alert--warn mt-2">
                    No items found for <b>{userId}</b>. Available userIds:{" "}
                    <b>{availableUserIds.slice(0, 8).join(", ") || "—"}</b>
                    {availableUserIds.length > 8 && <span> ...</span>}
                  </div>
                )}
              </div>

              <div className="fe-form__group">
                <label>Select Item</label>
                <select
                  value={selectedFoodId}
                  onChange={(e) => setSelectedFoodId(e.target.value)}
                  disabled={loading || userFoods.length === 0}
                >
                  {userFoods.length === 0 ? (
                    <option value="">No items for this user</option>
                  ) : (
                    userFoods.map((f) => (
                      <option key={f._id} value={f._id}>
                        {f.foodName || f.itemName} ({f.itemName})
                      </option>
                    ))
                  )}
                </select>
              </div>
            </div>
          </div>

          {/* TOP PRIORITY LIST */}
          <div className="fe-card mt-4">
            <h3 className="fe-section__title mb-3">Top Priority to Consume (by SCP)</h3>

            {priorityList.length === 0 ? (
              <div className="fe-muted">No predicted items yet for this user.</div>
            ) : (
              <table className="fe-table">
                <thead>
                  <tr>
                    <th>Food</th>
                    <th>Final Expiry</th>
                    <th>Days Left</th>
                    <th>SCP</th>
                  </tr>
                </thead>
                <tbody>
                  {priorityList.map((f) => (
                    <tr key={f._id}>
                      <td>
                        <div className="fe-strong">{f.foodName || f.itemName}</div>
                        <div className="fe-muted fe-small">{f.itemName}</div>
                      </td>
                      <td>{fmtDate(f.finalExpiryDate)}</td>
                      <td>{f.daysLeftAtSave ?? "—"}</td>
                      <td>
                        {f.scpPriorityScore ?? "—"}
                        {f.scpPriorityScore !== null && f.scpPriorityScore !== undefined && (
                          <span className="fe-muted fe-small"> ({scpLabel(f.scpPriorityScore)})</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* SELECTED ITEM SUMMARY */}
          <div className="fe-card mt-4">
            <h3 className="fe-section__title mb-3">Selected Item Summary</h3>

            {!selectedFood ? (
              <div className="fe-muted">Select an item to view history.</div>
            ) : (
              <div className="fe-result-box">
                <div className="fe-strong">{selectedFood.foodName || selectedFood.itemName}</div>
                <div className="fe-muted fe-small">
                  Item: {selectedFood.itemName} • Category: {selectedFood.category} • Storage:{" "}
                  {selectedFood.storageType}
                </div>
                <div className="fe-muted fe-small">
                  Purchase: {fmtDate(selectedFood.purchaseDate)} • Printed expiry:{" "}
                  {fmtDate(selectedFood.printedExpiryDate)}
                </div>

                {/* ✅ PP2 optional: show environment (if saved) */}
                <div className="fe-muted fe-small mt-1">
                  Environment: Region {safeText(selectedFood.region)} • Temp{" "}
                  {selectedFood.storage_temperature_c ?? "—"}°C • Hum{" "}
                  {selectedFood.storage_humidity_pct ?? "—"}%
                </div>

                <hr />

                <p>
                  <strong>Baseline Expiry:</strong> {fmtDate(selectedFood.baselineExpiryDate)}
                </p>
                <p>
                  <strong>Personalized Expiry:</strong> {fmtDate(selectedFood.personalizedExpiryDate)}
                </p>
                <p>
                  <strong>Final Expiry (after printed cap):</strong> {fmtDate(selectedFood.finalExpiryDate)}
                </p>
                <p>
                  <strong>SCP (stored):</strong> {selectedFood.scpPriorityScore ?? "—"}{" "}
                  {selectedFood.scpPriorityScore !== null && selectedFood.scpPriorityScore !== undefined && (
                    <span className="fe-muted fe-small">({scpLabel(selectedFood.scpPriorityScore)})</span>
                  )}
                </p>
              </div>
            )}
          </div>

          {/* HISTORY TABLE */}
          <div className="fe-card mt-4">
            <h3 className="fe-section__title mb-3">Prediction History (Newest → Oldest)</h3>

            {!selectedFood ? (
              <div className="fe-muted">Select an item to see prediction history.</div>
            ) : history.length === 0 ? (
              <div className="fe-muted">
                No prediction history yet. Go to <b>Inventory</b> and click <b>Predict</b>.
              </div>
            ) : (
              <table className="fe-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Baseline</th>
                    <th>Personalized</th>
                    <th>Final</th>
                    <th>Days Left</th>
                    <th>SCP</th>
                    <th>Printed Cap</th>
                    {/* ✅ PP2: show region/temp/humidity per prediction */}
                    <th>Environment</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h, idx) => (
                    <tr key={idx}>
                      <td className="fe-small">{h.ts ? new Date(h.ts).toLocaleString() : "—"}</td>

                      <td>
                        <div className="fe-small">{fmtDate(h.baseline_expiry_date)}</div>
                        <div className="fe-muted fe-small">{fmtNum(h.baseline_days)} days</div>
                      </td>

                      <td>
                        {h.personalization_enabled ? (
                          <>
                            <div className="fe-small">{fmtDate(h.personalized_expiry_date)}</div>
                            <div className="fe-muted fe-small">{fmtNum(h.personalized_days)} days</div>
                          </>
                        ) : (
                          <span className="fe-muted fe-small">Not enabled</span>
                        )}
                      </td>

                      <td>
                        <div className="fe-small">{fmtDate(h.final_expiry_date)}</div>
                        <div className="fe-muted fe-small">
                          Printed: {fmtDate(h.printed_expiry_date)}
                        </div>
                      </td>

                      <td>{h.days_left ?? "—"}</td>

                      <td>
                        {h.scp ?? "—"}{" "}
                        {h.scp !== null && h.scp !== undefined && (
                          <span className="fe-muted fe-small">({scpLabel(h.scp)})</span>
                        )}
                      </td>

                      <td>{h.printed_cap_applied ? "Yes" : "No"}</td>

                      <td className="fe-small">
                        <div>Region: {safeText(h.region)}</div>
                        <div className="fe-muted fe-small">
                          Temp: {h.storage_temperature_c ?? "—"}°C • Hum: {h.storage_humidity_pct ?? "—"}%
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* PP1 explanation block */}
          <div className="fe-card mt-4">
            <h3 className="fe-section__title mb-2">How to use the Expiry Predictor?</h3>
            <div className="fe-muted fe-small">
              1) Add item → stored in inventory. <br />
              2) Predict from Inventory → system calculates <b>baseline</b> (AEIF), then if user has ≥ 5 feedbacks it applies{" "}
              <b>AED personalization</b>. <br />
              3) If printed expiry exists → final date is <b>capped</b> for safety. <br />
              4) Then SCP ranks urgency using <b>days left</b>. <br />
              5) Every prediction is stored in <b>predictionHistory</b> so we can prove personalization over time.
              <br />
              6) (PP2) Predictions also store <b>environment</b> (region, temperature, humidity) to justify real-world usage.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}