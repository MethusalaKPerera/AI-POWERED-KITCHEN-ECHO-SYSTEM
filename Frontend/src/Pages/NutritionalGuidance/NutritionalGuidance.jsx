import React, { useState } from "react";

import DashboardHome from "./components/DashboardHome";
import UserDetailsForm from "./components/UserDetailsForm";
import MealLogger from "./components/MealLogger";
import NutritionTracker from "./components/NutritionTracker";
import PredictiveAnalytics from "./components/PredictiveAnalytics";

import "./NutritionalGuidance.css";

const NutritionalGuidance = () => {
  const [activeTab, setActiveTab] = useState("dashboard");

  const userId = "demo";

  const renderComponent = () => {
    switch (activeTab) {
      case "dashboard":
        return <DashboardHome userId={userId} />;
      case "profile":
        return <UserDetailsForm userId={userId} />;
      case "meal-logger":
        return <MealLogger userId={userId} />;
      case "nutrition-tracker":
        return <NutritionTracker userId={userId} />;
      case "predictive-analytics":
        return <PredictiveAnalytics userId={userId} />;
      default:
        return <DashboardHome userId={userId} />;
    }
  };

  return (
    <div className="nutritional-guidance-container">
      {/* Sidebar — uses ng- prefixed classes to avoid bleed-in */}
      <aside className="ng-sidebar">
        <div className="ng-sidebar-header">
          <div className="ng-logo-icon">🥗</div>
          <h2>Nutrition AI</h2>
          <p className="ng-tagline">Health Guide</p>
        </div>

        <nav className="ng-sidebar-nav">
          <div
            className={`ng-nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            <span className="ng-nav-icon">📊</span>
            <span>Dashboard</span>
          </div>

          <div
            className={`ng-nav-item ${activeTab === "profile" ? "active" : ""}`}
            onClick={() => setActiveTab("profile")}
          >
            <span className="ng-nav-icon">👤</span>
            <span>User Profile</span>
          </div>

          <div
            className={`ng-nav-item ${activeTab === "meal-logger" ? "active" : ""}`}
            onClick={() => setActiveTab("meal-logger")}
          >
            <span className="ng-nav-icon">🍽️</span>
            <span>Meal Logger</span>
          </div>

          <div
            className={`ng-nav-item ${activeTab === "nutrition-tracker" ? "active" : ""
              }`}
            onClick={() => setActiveTab("nutrition-tracker")}
          >
            <span className="ng-nav-icon">📈</span>
            <span>Nutrition Tracker</span>
          </div>

          <div
            className={`ng-nav-item ${activeTab === "predictive-analytics" ? "active" : ""
              }`}
            onClick={() => setActiveTab("predictive-analytics")}
          >
            <span className="ng-nav-icon">🧠</span>
            <span>Predictive Analytics</span>
          </div>
        </nav>

        <div className="ng-sidebar-footer">
          <div className="ng-health-badge">
            <span className="ng-badge-icon">💪</span>
            <div>
              <div className="ng-badge-title">AI Health</div>
              <div className="ng-badge-subtitle">Personal Coach</div>
            </div>
          </div>

          <div className="ng-dev-userid">
            <span className="ng-dev-label">User:</span> {userId}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="ng-main-content">{renderComponent()}</div>
    </div>
  );
};

export default NutritionalGuidance;
