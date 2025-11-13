import React, { useState } from 'react';
import DashboardHome from './components/DashboardHome';
import UserDetailsForm from './components/UserDetailsForm';
import MealLogger from './components/MealLogger';
import NutritionTracker from './components/NutritionTracker';
import MedicationAlerts from './components/MedicationAlerts';
import PredictiveAnalytics from './components/PredictiveAnalytics';
import Settings from './components/Settings';
import './NutritionalGuidance.css';

const NutritionalGuidance = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderComponent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardHome />;
      case 'profile':
        return <UserDetailsForm />;
      case 'meal-logger':
        return <MealLogger />;
      case 'nutrition-tracker':
        return <NutritionTracker />;
      case 'medication-alerts':
        return <MedicationAlerts />;
      case 'predictive-analytics':
        return <PredictiveAnalytics />;
      case 'settings':
        return <Settings />;
      default:
        return <DashboardHome />;
    }
  };

  return (
    <div className="nutritional-guidance-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-icon">🥗</div>
          <h2>Nutrition AI</h2>
          <p className="tagline">Health Guide</p>
        </div>

        <nav className="sidebar-nav">
          <div 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span className="nav-icon">📊</span>
            <span>Dashboard</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            <span className="nav-icon">👤</span>
            <span>User Profile</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'meal-logger' ? 'active' : ''}`}
            onClick={() => setActiveTab('meal-logger')}
          >
            <span className="nav-icon">🍽️</span>
            <span>Meal Logger</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'nutrition-tracker' ? 'active' : ''}`}
            onClick={() => setActiveTab('nutrition-tracker')}
          >
            <span className="nav-icon">📈</span>
            <span>Nutrition Tracker</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'medication-alerts' ? 'active' : ''}`}
            onClick={() => setActiveTab('medication-alerts')}
          >
            <span className="nav-icon">⚠️</span>
            <span>Medication Alerts</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'predictive-analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('predictive-analytics')}
          >
            <span className="nav-icon">🧠</span>
            <span>Predictive Analytics</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <span className="nav-icon">⚙️</span>
            <span>Settings</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="health-badge">
            <span className="badge-icon">💪</span>
            <div>
              <div className="badge-title">AI Health</div>
              <div className="badge-subtitle">Personal Coach</div>
            </div>
          </div>
        </div>
      </aside>
      
      {/* Main Content */}
      <div className="main-content">
        {renderComponent()}
      </div>
    </div>
  );
};

export default NutritionalGuidance;