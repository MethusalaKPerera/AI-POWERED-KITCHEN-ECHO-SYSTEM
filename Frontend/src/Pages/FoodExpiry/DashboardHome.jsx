// src/Pages/FoodExpiry/DashboardHome.jsx
import React, { useEffect, useMemo, useState } from "react";
import { NavLink } from "react-router-dom";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { getAllFoods } from "../../api/foodApi.js";
import "./foodexpiry.css";

function parseDateSafe(v) {
  if (!v) return null;
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? null : d;
}

function daysUntil(expiry, now) {
  const ms = expiry.getTime() - now.getTime();
  return Math.ceil(ms / (1000 * 60 * 60 * 24));
}

function pickExpiry(f) {
  return parseDateSafe(
    f.finalExpiryDate || f.predictedExpiryDate || f.predicted_expiry_date
  );
}

function normalizeName(f) {
  return (
    f.foodName ||
    f.food_name ||
    f.item_name ||
    f.itemName ||
    "Unknown item"
  );
}

export default function DashboardHome() {
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await getAllFoods();
        setFoods(Array.isArray(data) ? data : []);
        setApiError("");
      } catch (err) {
        setApiError(err?.message || "Failed to load inventory.");
        setFoods([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const computed = useMemo(() => {
    const now = new Date();

    let expiringSoon = 0; // <= 3 days
    let expired = 0;
    let safe = 0; // > 3 days
    const storageCounts = { fridge: 0, freezer: 0, pantry: 0, other: 0 };

    const items = foods
      .map((f) => {
        const expiry = pickExpiry(f);
        const d = expiry ? daysUntil(expiry, now) : null;
        return { raw: f, expiry, days: d };
      })
      .filter((x) => x.expiry);

    for (const x of items) {
      if (x.days < 0) expired += 1;
      else if (x.days <= 3) expiringSoon += 1;
      else safe += 1;

      const st = String(
        x.raw.storage_type || x.raw.storageType || x.raw.storage || ""
      ).toLowerCase();

      if (st.includes("fridge") || st.includes("refrig")) storageCounts.fridge += 1;
      else if (st.includes("freezer")) storageCounts.freezer += 1;
      else if (st.includes("pantry")) storageCounts.pantry += 1;
      else storageCounts.other += 1;
    }

    const topUseFirst = [...items]
      .sort((a, b) => (a.days ?? 999999) - (b.days ?? 999999))
      .slice(0, 6);

    return {
      total: foods.length,
      withExpiry: items.length,
      expiringSoon,
      expired,
      safe,
      storageCounts,
      topUseFirst,
    };
  }, [foods]);

  return (
    <div className="fe-layout">
      <Sidebar />

      <div className="fe-main">
        <Topbar title="Food Expiry Dashboard" />

        <div className="fe-main__content">
          {loading && <div className="fehome-loading">Loading dashboard…</div>}

          {!loading && apiError && (
            <div className="fe-alert fe-alert--error">{apiError}</div>
          )}

          {!loading && !apiError && (
            <div className="fehome">
              {/* HERO */}
              <section className="fehome-hero">
                <div className="fehome-hero-left">
                  <div className="fehome-hero-badge">
                    Behavioral Food Expiry Predictor • AEIF + AED + SCP
                  </div>

                  <h2 className="fehome-hero-title">
                    Track expiry early, <span>reduce food waste</span>
                  </h2>

                  <p className="fehome-hero-sub">
                    Your inventory is analyzed using predicted expiry dates and priority ranking to
                    help you use the right items first.
                  </p>

                  <div className="fehome-hero-actions">
                    <NavLink className="fehome-btn fehome-btn--primary" to="/food-expiry/inventory">
                      View Inventory
                    </NavLink>
                    <NavLink className="fehome-btn" to="/food-expiry/add">
                      Add Food
                    </NavLink>
                    <NavLink className="fehome-btn" to="/food-expiry/predict">
                      Predict Expiry
                    </NavLink>
                    <NavLink className="fehome-btn" to="/food-expiry/use">
                      How to use the Personalized Expiry Predictor
                    </NavLink>
                  </div>

                  <div className="fehome-hero-kpis">
                    <div className="fehome-kpi">
                      <div className="fehome-kpi__label">Total Items</div>
                      <div className="fehome-kpi__value">{computed.total}</div>
                    </div>
                    <div className="fehome-kpi fehome-kpi--warn">
                      <div className="fehome-kpi__label">Expiring ≤ 3 days</div>
                      <div className="fehome-kpi__value">{computed.expiringSoon}</div>
                    </div>
                    <div className="fehome-kpi fehome-kpi--bad">
                      <div className="fehome-kpi__label">Expired</div>
                      <div className="fehome-kpi__value">{computed.expired}</div>
                    </div>
                    <div className="fehome-kpi fehome-kpi--good">
                      <div className="fehome-kpi__label">Safe</div>
                      <div className="fehome-kpi__value">{computed.safe}</div>
                    </div>
                  </div>

                  <div className="fehome-hero-note">
                    <span className="fehome-dot" />
                    Tip: add feedback in <b>Feedback Trainer</b> to improve personalization.
                  </div>
                </div>

                <div className="fehome-hero-right" aria-hidden="true">
                  <div className="fehome-orb fehome-orb--a" />
                  <div className="fehome-orb fehome-orb--b" />
                  <div className="fehome-orb fehome-orb--c" />
                </div>
              </section>

              {/* STATS GRID */}
              <section className="fehome-stats">
                <div className="fehome-stat">
                  <div className="fehome-stat__icon">📦</div>
                  <div className="fehome-stat__meta">
                    <div className="fehome-stat__label">Items with predicted expiry</div>
                    <div className="fehome-stat__value">{computed.withExpiry}</div>
                    <div className="fehome-stat__sub">Based on backend predicted fields</div>
                  </div>
                </div>

                <div className="fehome-stat fehome-stat--warn">
                  <div className="fehome-stat__icon">⏳</div>
                  <div className="fehome-stat__meta">
                    <div className="fehome-stat__label">High priority items</div>
                    <div className="fehome-stat__value">{computed.expiringSoon}</div>
                    <div className="fehome-stat__sub">Use these first (≤ 3 days)</div>
                  </div>
                </div>

                <div className="fehome-stat fehome-stat--bad">
                  <div className="fehome-stat__icon">⚠️</div>
                  <div className="fehome-stat__meta">
                    <div className="fehome-stat__label">Expired items</div>
                    <div className="fehome-stat__value">{computed.expired}</div>
                    <div className="fehome-stat__sub">Review and discard safely</div>
                  </div>
                </div>

                <div className="fehome-stat fehome-stat--good">
                  <div className="fehome-stat__icon">✅</div>
                  <div className="fehome-stat__meta">
                    <div className="fehome-stat__label">Safe items</div>
                    <div className="fehome-stat__value">{computed.safe}</div>
                    <div className="fehome-stat__sub">More than 3 days remaining</div>
                  </div>
                </div>
              </section>

              {/* PANELS */}
              <section className="fehome-panels">
                <div className="fehome-panel">
                  <div className="fehome-panel__head">
                    <h3 className="fehome-panel__title">Top items to use first</h3>
                    <span className="fehome-panel__pill">SCP priority view</span>
                  </div>

                  {computed.topUseFirst.length === 0 ? (
                    <div className="fehome-empty">
                      No predicted expiry dates found yet. Add items or run prediction.
                    </div>
                  ) : (
                    <ul className="fehome-list">
                      {computed.topUseFirst.map((x, idx) => {
                        const name = normalizeName(x.raw);
                        const d = x.days ?? 0;
                        const tag =
                          d < 0 ? "Expired" : d === 0 ? "Today" : `${d} day${d === 1 ? "" : "s"}`;
                        const tone = d < 0 ? "bad" : d <= 3 ? "warn" : "good";
                        return (
                          <li key={x.raw._id || `${name}-${idx}`} className="fehome-list__item">
                            <span className={`fehome-rank fehome-rank--${tone}`}>{idx + 1}</span>
                            <div className="fehome-list__main">
                              <div className="fehome-list__name">{name}</div>
                              <div className="fehome-list__meta">
                                Storage:{" "}
                                {String(
                                  x.raw.storage_type || x.raw.storageType || "pantry"
                                ).toUpperCase()}
                              </div>
                            </div>
                            <span className={`fehome-tag fehome-tag--${tone}`}>{tag}</span>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </div>

                <div className="fehome-panel">
                  <div className="fehome-panel__head">
                    <h3 className="fehome-panel__title">Storage overview</h3>
                    <span className="fehome-panel__pill">Where items are stored</span>
                  </div>

                  <div className="fehome-storage">
                    <div className="fehome-storage__row">
                      <span className="fehome-storage__label">Fridge</span>
                      <span className="fehome-storage__value">{computed.storageCounts.fridge}</span>
                    </div>
                    <div className="fehome-storage__row">
                      <span className="fehome-storage__label">Freezer</span>
                      <span className="fehome-storage__value">{computed.storageCounts.freezer}</span>
                    </div>
                    <div className="fehome-storage__row">
                      <span className="fehome-storage__label">Pantry</span>
                      <span className="fehome-storage__value">{computed.storageCounts.pantry}</span>
                    </div>
                    {computed.storageCounts.other > 0 && (
                      <div className="fehome-storage__row">
                        <span className="fehome-storage__label">Other</span>
                        <span className="fehome-storage__value">{computed.storageCounts.other}</span>
                      </div>
                    )}
                  </div>

                  <div className="fehome-storage-note">
                    Fridge/freezer typically last longer — your model personalization (AED) adapts
                    based on feedback and usage patterns.
                  </div>
                </div>
              </section>

              {/* FEATURE CARDS */}
              <section className="fehome-features">
                <div className="fehome-feature">
                  <h4 className="fehome-feature__title">Base Expiry Intelligence</h4>
                  <p className="fehome-feature__text">
                    Uses domain expiry ranges by item + storage type as a strong baseline.
                  </p>
                  <ul className="fehome-feature__list">
                    <li>Category-aware fallback</li>
                    <li>Storage-specific baselines</li>
                    <li>Safety bounding rules</li>
                  </ul>
                </div>

                <div className="fehome-feature">
                  <h4 className="fehome-feature__title">AED Personalization</h4>
                  <p className="fehome-feature__text">
                    Adjusts predicted expiry using your feedback and behavior to be user-specific.
                  </p>
                  <ul className="fehome-feature__list">
                    <li>Item-level adjustments</li>
                    <li>Category fallback</li>
                    <li>Prevents extreme shifts</li>
                  </ul>
                </div>

                <div className="fehome-feature">
                  <h4 className="fehome-feature__title">SCP Priority Ranking</h4>
                  <p className="fehome-feature__text">
                    Turns expiry predictions into a clear “use-first” list to reduce waste.
                  </p>
                  <ul className="fehome-feature__list">
                    <li>Expiring-first ordering</li>
                    <li>Highlights critical items</li>
                    <li>Easy daily actions</li>
                  </ul>
                </div>

                <div className="fehome-feature">
                  <h4 className="fehome-feature__title">Feedback Trainer</h4>
                  <p className="fehome-feature__text">
                    Learns from real outcomes (used-before-expiry / spoiled) for better accuracy.
                  </p>
                  <ul className="fehome-feature__list">
                    <li>Improves personalization</li>
                    <li>Better future predictions</li>
                    <li>Transparent learning loop</li>
                  </ul>
                </div>
              </section>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
