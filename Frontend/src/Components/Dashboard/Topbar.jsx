// src/Components/Dashboard/Topbar.jsx
import React from "react";
import "./dashboard.css";

export default function Topbar({ title = "Dashboard", badge = "AI-Powered" }) {
  const username = localStorage.getItem("FE_NAME") || "User";
  const role = localStorage.getItem("FE_ROLE") || "Food Expiry";

  return (
    <header className="ng-topbar">
      <div className="ng-topbar-left">
        <h1 className="ng-topbar-title">{title}</h1>
        {badge ? <span className="ng-topbar-pill">{badge}</span> : null}
      </div>

      <div className="ng-topbar-right">
        <div className="ng-avatar">{String(username).slice(0, 1).toUpperCase()}</div>
        <div className="ng-user">
          <div className="ng-user-name">{username}</div>
          <div className="ng-user-role">{role}</div>
        </div>
      </div>
    </header>
  );
}
