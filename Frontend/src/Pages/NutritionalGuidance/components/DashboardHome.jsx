import React from 'react';
import '../DashboardHome.css';

const DashboardHome = () => {
  return (
    <div className="dashboard-home">
      {/* Welcome Section */}
      <div className="welcome-section">
        <div className="welcome-content">
          <div className="welcome-icon">🥗</div>
          <h1>Welcome to Nutritional Guide</h1>
          <p className="subtitle">AI-Powered Predictive Health Intervention System</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-info">
            <h3>Nutrition Score</h3>
            <p className="stat-value">87%</p>
            <p className="stat-label">Excellent</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-info">
            <h3>Daily Energy</h3>
            <p className="stat-value">2,150</p>
            <p className="stat-label">Calories</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-info">
            <h3>Goals Achieved</h3>
            <p className="stat-value">12/15</p>
            <p className="stat-label">This Week</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🔮</div>
          <div className="stat-info">
            <h3>AI Predictions</h3>
            <p className="stat-value">3</p>
            <p className="stat-label">Health Insights</p>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="features-grid">
        <div className="card">
          <h3>🎯 Predictive Analytics</h3>
          <p>Get early warnings about potential micronutrient deficiencies 2-3 weeks in advance using our advanced AI models.</p>
          <ul>
            <li>✓ Machine Learning predictions</li>
            <li>✓ Personalized risk assessment</li>
            <li>✓ Preventive recommendations</li>
          </ul>
        </div>

        <div className="card">
          <h3>⏰ Circadian Nutrition</h3>
          <p>Optimize your meal timing based on your biological clock, work schedule, and sleep patterns for maximum metabolic efficiency.</p>
          <ul>
            <li>✓ Biological rhythm alignment</li>
            <li>✓ Energy optimization</li>
            <li>✓ Sleep quality improvement</li>
          </ul>
        </div>

        <div className="card">
          <h3>⚠️ Medication Safety</h3>
          <p>Real-time alerts for food-drug interactions to ensure your dietary choices don't interfere with medications.</p>
          <ul>
            <li>✓ Drug interaction database</li>
            <li>✓ Instant safety alerts</li>
            <li>✓ Alternative suggestions</li>
          </ul>
        </div>

        <div className="card">
          <h3>📈 Goal Tracking</h3>
          <p>Personalized nutrition plans tailored to your fitness goals - weight loss, muscle gain, or energy enhancement.</p>
          <ul>
            <li>✓ Custom goal setting</li>
            <li>✓ Progress monitoring</li>
            <li>✓ Adaptive recommendations</li>
          </ul>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="action-buttons">
          <button className="btn-primary">Log Today's Meals</button>
          <button className="btn-primary">Check Medication Alerts</button>
          <button className="btn-primary">View Nutrition Report</button>
          <button className="btn-primary">Update Profile</button>
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;
