import React, { useState } from 'react';
import './MealPlanner.css'; // Import the new CSS file

function MealPlanner() {
  const [numPeople, setNumPeople] = useState(1);
  const [mealPlan, setMealPlan] = useState({
    monday: { breakfast: '', lunch: '', dinner: '' },
    tuesday: { breakfast: '', lunch: '', dinner: '' },
    wednesday: { breakfast: '', lunch: '', dinner: '' },
    thursday: { breakfast: '', lunch: '', dinner: '' },
    friday: { breakfast: '', lunch: '', dinner: '' },
    saturday: { breakfast: '', lunch: '', dinner: '' },
    sunday: { breakfast: '', lunch: '', dinner: '' }
  });
  const [groceryList, setGroceryList] = useState(null);
  const [activeSection, setActiveSection] = useState('planner');
  const popularRecipes = [
    'Rice & Curry', 'Chicken Curry', 'Dhal Curry', 'Fish Curry',
    'Kottu Roti', 'Hoppers', 'String Hoppers', 'Egg Roti',
    'Coconut Sambol', 'Parippu', 'Vegetable Curry'
  ];

  const generateGroceryList = async () => {
    try {
      // Mock data for now - will connect to backend later
      const mockGrocery = {
        vegetables: [
          { item: 'Onions', quantity: 500 * numPeople, unit: 'g' },
          { item: 'Tomatoes', quantity: 750 * numPeople, unit: 'g' },
          { item: 'Garlic', quantity: 100 * numPeople, unit: 'g' },
          { item: 'Green Chilies', quantity: 50 * numPeople, unit: 'g' }
        ],
        protein: [
          { item: 'Chicken', quantity: 1.5 * numPeople, unit: 'kg' },
          { item: 'Fish', quantity: 1 * numPeople, unit: 'kg' },
          { item: 'Eggs', quantity: 12 * numPeople, unit: 'pcs' }
        ],
        grains: [
          { item: 'Rice', quantity: 2 * numPeople, unit: 'kg' },
          { item: 'Wheat Flour', quantity: 500 * numPeople, unit: 'g' }
        ],
        spices: [
          { item: 'Curry Powder', quantity: 100 * numPeople, unit: 'g' },
          { item: 'Turmeric', quantity: 50 * numPeople, unit: 'g' },
          { item: 'Curry Leaves', quantity: 50 * numPeople, unit: 'g' }
        ],
        dairy: [
          { item: 'Coconut Milk', quantity: 800 * numPeople, unit: 'ml' },
          { item: 'Milk', quantity: 2 * numPeople, unit: 'L' }
        ]
      };
      setGroceryList(mockGrocery);
      setActiveSection('grocery');
    } catch (error) {
      console.error('Error generating grocery list:', error);
    }
  };

  const handleDaySelectChange = (day, mealType, value) => {
    setMealPlan(prev => ({
      ...prev,
      [day]: {
        ...prev[day],
        [mealType]: value
      }
    }));
  };

  return (
    <div className="meal-planner-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-icon">📅</div>
          <h2>Meal Planner</h2>
          <p className="tagline">Weekly Planning</p>
        </div>

        <nav className="sidebar-nav">
          <div
            className={`nav-item ${activeSection === 'planner' ? 'active' : ''}`}
            onClick={() => setActiveSection('planner')}
          >
            <span className="nav-icon">📋</span>
            <span>Meal Plan</span>
          </div>
          <div
            className={`nav-item ${activeSection === 'grocery' ? 'active' : ''} ${groceryList ? '' : 'disabled'}`}
            onClick={() => groceryList && setActiveSection('grocery')}
          >
            <span className="nav-icon">🛒</span>
            <span>Grocery List</span>
          </div>
          <div
            className="nav-item"
            onClick={() => window.location.href = '/cooking-assistant'}
          >
            <span className="nav-icon">🍳</span>
            <span>Cooking Assistant</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="sri-lankan-badge">
            <span className="flag">🇱🇰</span>
            <div>
              <div className="badge-title">Authentic Sri Lankan</div>
              <div className="badge-subtitle">Traditional Recipes</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="meal-planner-page">
        {activeSection === 'planner' && (
          <section className="planner-section">
            <div className="planner-header-card">
              <h1 className="main-title">Weekly Meal Planner</h1>
              <p className="subtitle">Plan your week, generate shopping list automatically 🥘</p>
            </div>

            <div className="people-selector-card">
              <label className="label">👥 Number of People:</label>
              <div className="selector-controls">
                <button
                  onClick={() => setNumPeople(Math.max(1, numPeople - 1))}
                  className="control-btn"
                >
                  -
                </button>
                <div className="people-count">
                  {numPeople}
                </div>
                <button
                  onClick={() => setNumPeople(numPeople + 1)}
                  className="control-btn"
                >
                  +
                </button>
              </div>
              <p className="serving-text">Serving Size Calculator</p>
            </div>

            <div className="weekly-plan-card">
              <h3 className="card-title"><span>📋</span> Weekly Meal Plan</h3>
              <div className="weekly-grid">
                {Object.keys(mealPlan).map((day) => (
                  <div key={day} className="day-card">
                    <h4 className="day-title">{day}</h4>
                    <div className="meal-selectors">
                      <select
                        onChange={(e) => handleDaySelectChange(day, 'breakfast', e.target.value)}
                        value={mealPlan[day].breakfast}
                        className="meal-select"
                      >
                        <option value="">🌅 Breakfast</option>
                        {popularRecipes.map((recipe, idx) => (
                          <option key={idx} value={recipe}>{recipe}</option>
                        ))}
                      </select>
                      <select
                        onChange={(e) => handleDaySelectChange(day, 'lunch', e.target.value)}
                        value={mealPlan[day].lunch}
                        className="meal-select"
                      >
                        <option value="">☀️ Lunch</option>
                        {popularRecipes.map((recipe, idx) => (
                          <option key={idx} value={recipe}>{recipe}</option>
                        ))}
                      </select>
                      <select
                        onChange={(e) => handleDaySelectChange(day, 'dinner', e.target.value)}
                        value={mealPlan[day].dinner}
                        className="meal-select"
                      >
                        <option value="">🌙 Dinner</option>
                        {popularRecipes.map((recipe, idx) => (
                          <option key={idx} value={recipe}>{recipe}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={generateGroceryList}
              className="generate-btn primary"
            >
              🛒 Generate Grocery List
            </button>
          </section>
        )}

        {activeSection === 'grocery' && groceryList && (
          <section className="grocery-section">
            <div className="grocery-header-card">
              <h2 className="main-title">🛒 Your Grocery List</h2>
              <p className="subtitle">For {numPeople} {numPeople === 1 ? 'person' : 'people'} • 7 days</p>
            </div>

            <div className="grocery-grid">
              {Object.entries(groceryList).map(([category, items]) => (
                <div key={category} className="grocery-category-card">
                  <h3 className="category-title">
                    {category === 'vegetables' && '🥬'}
                    {category === 'protein' && '🍗'}
                    {category === 'grains' && '🌾'}
                    {category === 'spices' && '🌶️'}
                    {category === 'dairy' && '🥛'}
                    {' '}{category}
                  </h3>
                  <ul className="grocery-items-list">
                    {items.map((item, idx) => (
                      <li key={idx} className="grocery-item">
                        <span className="item-name">{item.item}</span>
                        <span className="item-quantity">
                          {item.quantity} {item.unit}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            <div className="action-buttons">
              <button className="btn secondary">
                📧 Email List
              </button>
              <button className="btn primary">
                📱 Send to Phone
              </button>
              <button className="btn success">
                🖨️ Print
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default MealPlanner;