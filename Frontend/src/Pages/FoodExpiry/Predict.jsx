import React, { useEffect, useMemo, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { getAllFoods } from "../../api/foodApi.js";
import "./foodexpiry.css";

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

export default function Predict() {
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");

  // For PP1 demo, keep one user at a time
  const [userId, setUserId] = useState("demo-user");
  const [selectedFoodId, setSelectedFoodId] = useState("");

  async function load() {
    try {
      setLoading(true);
      setApiError("");
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

  // filter by user
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
                  Use user IDs (e.g., <b>U001</b> and <b>U002</b>) to show different personalization.
                </div>
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
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* PP1 explanation block */}
          <div className="fe-card mt-4">
            <h3 className="fe-section__title mb-2">How to Explain to Panel (1 minute)</h3>
            <div className="fe-muted fe-small">
              1) Add item → stored in inventory. <br />
              2) Predict from Inventory → system calculates <b>baseline</b> (AEIF), then if user has ≥ 5 feedbacks it applies <b>AED personalization</b>. <br />
              3) If printed expiry exists → final date is <b>capped</b> for safety. <br />
              4) Then SCP ranks urgency using <b>days left</b>. <br />
              5) Every prediction is stored in <b>predictionHistory</b> so we can prove personalization over time.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
