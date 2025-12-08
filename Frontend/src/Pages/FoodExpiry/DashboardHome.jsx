// src/Pages/FoodExpiry/DashboardHome.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import StatCard from "../../Components/Dashboard/Statcard.jsx";
import { getAllFoods } from "../../api/foodApi"; 
import "./foodexpiry.css";

export default function DashboardHome() {
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await getAllFoods();
        setFoods(data || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  return (
    <div className="dashboard-container">
      <Sidebar />
      <div className="dashboard-main">
        <Topbar />

        {loading ? (
          <p>Loading...</p>
        ) : error ? (
          <p className="error">{error}</p>
        ) : (
          <>
            <div className="stats-row">
              <StatCard title="Total Items" value={foods.length} />
              <StatCard title="Expiring Soon" value={foods.filter(f => f.soon).length} />
              <StatCard title="Expired" value={foods.filter(f => f.expired).length} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
