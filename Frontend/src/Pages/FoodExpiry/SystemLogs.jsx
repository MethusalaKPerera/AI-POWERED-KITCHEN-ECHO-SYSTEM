// src/Pages/FoodExpiry/SystemLogs.jsx
import React from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import "./foodExpiry.css";

export default function SystemLogs() {
  return (
    <div className="fe-layout">
      <Sidebar />
      <div className="fe-main">
        <Topbar title="System Logs" />
        <div className="fe-main__content">
          <div className="fe-card">
            <h2 className="fe-section__title mb-4">System Events</h2>
            <p>
              For now this is a placeholder. You can later connect this to a{" "}
              <code>/logs</code> endpoint or Mongo collection and render recent
              events such as prediction calls, feedback updates, and errors.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
