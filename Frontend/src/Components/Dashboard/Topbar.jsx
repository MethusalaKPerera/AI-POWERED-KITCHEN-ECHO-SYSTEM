// src/Components/Dashboard/Topbar.jsx
import React from "react";
import "./dashboard.css";

export default function Topbar({ title = "Dashboard" }) {
  return (
    <header className="fe-topbar">
      <h1 className="fe-topbar__title">{title}</h1>

      <div className="fe-topbar__right">
        <span className="fe-topbar__badge">Expiry turns easier!</span>
        <div className="fe-topbar__user">
          <div className="fe-avatar-circle">S</div>
          <div className="fe-topbar__user-text">
            <span className="fe-topbar__username">AI-Powered Kitchen Ecosystem</span>
            <span className="fe-topbar__role">Personalized Food Expiry Prediction</span>
          </div>
        </div>
      </div>
    </header>
  );
}
