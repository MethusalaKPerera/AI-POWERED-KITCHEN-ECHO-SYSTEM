// src/Pages/FoodExpiry/UserProfile.jsx
import React, { useState } from "react";
import Sidebar from "../../Components/Dashboard/Sidebar.jsx";
import Topbar from "../../Components/Dashboard/Topbar.jsx";
import "./foodExpiry.css";

export default function UserProfile() {
  const [userId, setUserId] = useState("demo-user");
  const [region, setRegion] = useState("lowland");

  // Right now these are client-only; you can later POST to a user endpoint
  function handleSubmit(e) {
    e.preventDefault();
    alert(
      `Profile preferences saved locally.\nUser: ${userId}\nRegion: ${region}`
    );
  }

  return (
    <div className="fe-layout">
      <Sidebar />
      <div className="fe-main">
        <Topbar title="User Profile" />
        <div className="fe-main__content">
          <form className="fe-card fe-form fe-form--medium" onSubmit={handleSubmit}>
            <h2 className="fe-section__title mb-4">Profile Settings</h2>

            <div className="fe-form__group">
              <label>Default User ID</label>
              <input
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
              />
            </div>

            <div className="fe-form__group">
              <label>Region (for climate assumptions)</label>
              <select value={region} onChange={(e) => setRegion(e.target.value)}>
                <option value="lowland">Lowland</option>
                <option value="coastal">Coastal</option>
                <option value="highland">Highland</option>
              </select>
            </div>

            <button className="fe-btn fe-btn--primary mt-4" type="submit">
              Save Preferences
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
