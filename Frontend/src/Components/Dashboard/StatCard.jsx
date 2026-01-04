// src/Components/Dashboard/StatCard.jsx
import React from "react";
import "./dashboard.css";

export default function StatCard({ label, value, sublabel, tone = "default" }) {
  return (
    <div className={`fe-card fe-card--stat fe-card--${tone}`}>
      <div className="fe-card__label">{label}</div>
      <div className="fe-card__value">{value}</div>
      {sublabel && <div className="fe-card__sublabel">{sublabel}</div>}
    </div>
  );
}
