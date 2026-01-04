import React, { useEffect, useMemo, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import StatCard from "../../Components/Dashboard/Statcard.jsx";
import { getAllFoods } from "../../api/foodApi.js";
import "./foodexpiry.css";

function parseDateSafe(v) {
  if (!v) return null;
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? null : d;
}

function daysDiff(from, to) {
  const ms = to.getTime() - from.getTime();
  return Math.ceil(ms / (1000 * 60 * 60 * 24));
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
      } catch (err) {
        setApiError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const stats = useMemo(() => {
    const now = new Date();
    let expiringSoon = 0;
    let expired = 0;

    for (const f of foods) {
      const expiry = parseDateSafe(f.predictedExpiryDate || f.predicted_expiry_date);
      if (!expiry) continue;

      const d = daysDiff(now, expiry);
      if (d < 0) expired += 1;
      else if (d <= 3) expiringSoon += 1; // “soon” = within 3 days
    }

    return {
      total: foods.length,
      expiringSoon,
      expired,
    };
  }, [foods]);

  return (
    <div className="dashboard-container">
      <Sidebar />
      <div className="dashboard-main">
        <Topbar title="Food Expiry Dashboard" />

        <div className="fe-main__content">
          {loading && <p>Loading...</p>}
          {!loading && apiError && <div className="fe-alert fe-alert--error">{apiError}</div>}

          {!loading && !apiError && (
            <div className="stats-row">
              <StatCard title="Total Items" value={stats.total} />
              <StatCard title="Expiring Soon (≤ 3 days)" value={stats.expiringSoon} />
              <StatCard title="Expired" value={stats.expired} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
