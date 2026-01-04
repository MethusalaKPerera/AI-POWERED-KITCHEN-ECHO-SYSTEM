// src/Components/Dashboard/Sidebar.jsx
import React from "react";
import { NavLink } from "react-router-dom";
import "./dashboard.css";

const navItems = [
  { to: "/food-expiry", label: "Overview" },
  { to: "/food-expiry/predict", label: "Predict Expiry" },
  { to: "/food-expiry/add", label: "Add Food" },
  { to: "/food-expiry/inventory", label: "Inventory" },
  { to: "/food-expiry/feedback", label: "Feedback Trainer" },
  { to: "/food-expiry/analytics", label: "Analytics" },
  { to: "/food-expiry/profile", label: "User Profile" },
  { to: "/food-expiry/logs", label: "System Logs" },
];

export default function Sidebar() {
  return (
    <aside className="fe-sidebar">
      <div className="fe-sidebar__brand">
        <span className="fe-logo-dot" />
        <span className="fe-brand-text">Food Expiry AI</span>
      </div>

      <nav className="fe-sidebar__nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              "fe-sidebar__link" + (isActive ? " fe-sidebar__link--active" : "")
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
