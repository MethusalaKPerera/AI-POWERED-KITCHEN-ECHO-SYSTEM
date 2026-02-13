// src/Components/Dashboard/Sidebar.jsx
import React from "react";
import { NavLink } from "react-router-dom";
import "./dashboard.css";

const navItems = [
  { to: "/food-expiry", icon: "🏠", label: "Dashboard" },
  { to: "/food-expiry/predict", icon: "🧠", label: "Predict Expiry" },
  { to: "/food-expiry/add", icon: "➕", label: "Add Food" },
  { to: "/food-expiry/inventory", icon: "📦", label: "Inventory" },
  { to: "/food-expiry/feedback", icon: "📝", label: "Feedback Trainer" },
  { to: "/food-expiry/analytics", icon: "📊", label: "Analytics" },
];

export default function Sidebar() {
  const userId = localStorage.getItem("FE_USER_ID") || "U001";

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-icon">🍃</div>
        <div className="sidebar-title">SmartKitchen</div>
        <div className="sidebar-subtitle">Food Expiry Module</div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="health-badge">
          <span className="badge-icon">✅</span>
          <div>
            <div className="badge-title">System Health</div>
            <div className="badge-subtitle">Backend Connected</div>
          </div>
        </div>

        <div className="dev-userid">
          <span className="dev-label">User:</span>
          <b>{userId}</b>
        </div>
      </div>
    </aside>
  );
}
