// src/Pages/FoodExpiry/Analytics.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import { getAllFoods } from "../../api/foodApi.js";
import "./foodexpiry.css";

export default function Analytics() {
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const data = await getAllFoods();
        setFoods(data || []);
      } catch (err) {
        setApiError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const byCategory = foods.reduce((acc, f) => {
    const cat = f.category || "unknown";
    acc[cat] = (acc[cat] || 0) + 1;
    return acc;
  }, {});

  const total = foods.length || 1;

  return (
    <div className="fe-layout">
      <Sidebar />
      <div className="fe-main">
        <Topbar title="Analytics" />
        <div className="fe-main__content">
          {apiError && <div className="fe-alert fe-alert--error">{apiError}</div>}

          <div className="fe-card">
            <h2 className="fe-section__title mb-4">Items by Category</h2>
            {loading && <p>Loading...</p>}
            {!loading && Object.keys(byCategory).length === 0 && (
              <p>No data available yet.</p>
            )}
            {!loading &&
              Object.entries(byCategory).map(([cat, count]) => {
                const pct = Math.round((count / total) * 100);
                return (
                  <div key={cat} className="fe-analytics-row">
                    <span className="fe-analytics-label">
                      {cat} ({count})
                    </span>
                    <div className="fe-analytics-bar">
                      <div
                        className="fe-analytics-bar__fill"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="fe-analytics-value">{pct}%</span>
                  </div>
                );
              })}
          </div>
        </div>
      </div>
    </div>
  );
}
