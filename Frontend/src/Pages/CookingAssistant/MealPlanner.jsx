import React, { useState, useRef } from 'react';
import './MealPlanner.css';
import LanguageSelector from '../../Components/LanguageSelector';
import { API_URL } from '../../config';

const SL_RECIPES = [
  'Rice & Curry', 'Chicken Curry', 'Dhal Curry (Parippu)', 'Fish Curry',
  'Kottu Roti', 'Hoppers (Appa)', 'String Hoppers (Idiyappam)', 'Egg Roti',
  'Coconut Sambol', 'Pol Roti', 'Vegetable Curry', 'Ambulthiyal (Sour Fish)',
  'Kiribath (Milk Rice)', 'Pittu', 'Lamprais', 'Kukul Mas Curry',
  'Brinjal Moju', 'Devilled Chicken', 'Prawn Curry', 'Egg Curry',
  'Beetroot Curry', 'Mushroom Curry', 'Pumpkin Curry', 'Leeks Curry',
  'Chickpea Curry (Kadala)', 'Polos Curry (Jackfruit)', 'Sardine Curry',
  'Ash Plantain Curry', 'Kiri Hodi', 'Mutton Curry', 'Rasam',
];

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
const MEALS = ['breakfast', 'lunch', 'dinner'];
const MEAL_ICONS = { breakfast: '🌅', lunch: '☀️', dinner: '🌙' };

export default function MealPlanner() {
  const [activeNav, setActiveNav] = useState('planner');
  const [activeTab, setActiveTab] = useState('dropdown');
  const [numPeople, setNumPeople] = useState(2);
  const [mealPlan, setMealPlan] = useState(
    Object.fromEntries(DAYS.map(d => [d, { breakfast: '', lunch: '', dinner: '' }]))
  );
  const [freeText, setFreeText] = useState('');
  const [planImage, setPlanImage] = useState(null);
  const [planImagePreview, setPlanImagePreview] = useState(null);
  const [groceryList, setGroceryList] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [parsedPlan, setParsedPlan] = useState(null);
  const fileRef = useRef();

  // ── Helpers ───────────────────────────────────────────────────────────────
  const setMeal = (day, meal, val) =>
    setMealPlan(p => ({ ...p, [day]: { ...p[day], [meal]: val } }));

  const dropdownMealCount = Object.values(mealPlan).flatMap(Object.values).filter(Boolean).length;

  // ── Parse text ────────────────────────────────────────────────────────────
  const parseTextPlan = async () => {
    if (!freeText.trim()) { setError('Please type your meal plan first!'); return; }
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_URL}/parse-meal-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: freeText }),
      });
      const data = await res.json();
      if (data.success && data.meal_plan) {
        setParsedPlan(data.meal_plan);
        await buildGroceryFromPlan(data.meal_plan);
      } else setError(data.error || 'Could not parse meal plan. Try being more specific.');
    } catch { setError('Cannot connect to backend.'); }
    finally { setLoading(false); }
  };

  // ── Parse image ───────────────────────────────────────────────────────────
  const parseImagePlan = async () => {
    if (!planImage) { setError('Please upload an image first!'); return; }
    setLoading(true); setError('');
    try {
      const fd = new FormData();
      fd.append('image', planImage);
      const res = await fetch(`${API_URL}/parse-meal-plan-image`, {
        method: 'POST', body: fd,
      });
      const data = await res.json();
      if (data.success && data.meal_plan) {
        setParsedPlan(data.meal_plan);
        await buildGroceryFromPlan(data.meal_plan);
      } else setError(data.error || 'Could not read meal plan from image.');
    } catch { setError('Cannot connect to backend.'); }
    finally { setLoading(false); }
  };

  // ── Build grocery from dropdown ───────────────────────────────────────────
  const buildGroceryFromDropdown = async () => {
    const selected = Object.values(mealPlan).flatMap(Object.values).filter(Boolean);
    if (selected.length === 0) { setError('Please add at least one meal!'); return; }
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_URL}/grocery-from-meals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meals: selected, num_people: numPeople }),
      });
      const data = await res.json();
      if (data.success) { setGroceryList(data.grocery); setActiveNav('grocery'); }
      else setError(data.error || 'Failed to generate grocery list.');
    } catch { setError('Cannot connect to backend.'); }
    finally { setLoading(false); }
  };

  // ── Build grocery from parsed plan ────────────────────────────────────────
  const buildGroceryFromPlan = async (plan) => {
    const meals = Object.values(plan)
      .flatMap(day => typeof day === 'object' ? Object.values(day) : [day])
      .filter(Boolean);
    try {
      const res = await fetch(`${API_URL}/grocery-from-meals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meals, num_people: numPeople }),
      });
      const data = await res.json();
      if (data.success) { setGroceryList(data.grocery); setActiveNav('grocery'); }
      else setError(data.error || 'Failed to build grocery list.');
    } catch { setError('Cannot connect to backend.'); }
  };

  const handlePrint = () => window.print();

  const onImageSelect = (file) => {
    if (!file) return;
    setPlanImage(file);
    setPlanImagePreview(URL.createObjectURL(file));
  };

  return (
    <div className="mp-root">

      {/* ── Sidebar ── */}
      <aside className="mp-sidebar">
        <div className="mp-logo">
          <span className="mp-logo-icon">📅</span>
          <div>
            <h2 className="mp-logo-title">Meal Planner</h2>
            <span className="mp-logo-sub">Weekly Planning</span>
          </div>
        </div>

        <nav className="mp-nav">
          {[
            { id: 'planner', icon: '📋', label: 'Meal Plan' },
            { id: 'grocery', icon: '🛒', label: 'Grocery List', disabled: !groceryList },
            { id: 'cooking', icon: '🍳', label: 'Cooking Assistant', link: '/cooking-assistant' },
          ].map(item => (
            <button
              key={item.id}
              className={`mp-nav-item ${activeNav === item.id ? 'active' : ''} ${item.disabled ? 'disabled' : ''}`}
              onClick={() => {
                if (item.disabled) return;
                if (item.link) { window.location.href = item.link; return; }
                setActiveNav(item.id);
              }}
            >
              <span className="mp-nav-icon">{item.icon}</span>
              <span>{item.label}</span>
              {item.id === 'grocery' && !groceryList && <span className="mp-lock">🔒</span>}
            </button>
          ))}
        </nav>

        {/* ── Language Selector ── */}
        <LanguageSelector />

        <div className="mp-sidebar-footer">
          <div className="mp-badge">
            <span>🇱🇰</span>
            <div>
              <div className="mp-badge-title">Authentic Sri Lankan</div>
              <div className="mp-badge-sub">Traditional Recipes</div>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="mp-main">

        {/* ══ PLANNER ══ */}
        {activeNav === 'planner' && (
          <>
            <div className="mp-hero">
              <div className="mp-hero-text">
                <p className="mp-hero-tag">SmartKitchen • Meal Planner</p>
                <h1 className="mp-hero-title">Plan your week,<br /><span className="mp-hero-accent">shop smarter</span></h1>
                <p className="mp-hero-desc">
                  Add meals by dropdown, free text, or upload a photo of your handwritten plan — we'll generate your grocery list automatically.
                </p>
              </div>
              <div className="mp-hero-visual">🗓️</div>
            </div>

            {/* People selector */}
            <div className="mp-people-card">
              <span className="mp-people-label">👥 Number of People</span>
              <div className="mp-people-controls">
                <button className="mp-people-btn" onClick={() => setNumPeople(p => Math.max(1, p - 1))}>−</button>
                <span className="mp-people-count">{numPeople}</span>
                <button className="mp-people-btn" onClick={() => setNumPeople(p => p + 1)}>+</button>
              </div>
              <span className="mp-people-hint">
                Ingredients will be scaled for {numPeople} {numPeople === 1 ? 'person' : 'people'}
              </span>
            </div>

            {/* Tabs */}
            <div className="mp-section">
              <div className="mp-tabs">
                {[
                  { id: 'dropdown', icon: '📋', label: 'Select Meals' },
                  { id: 'text', icon: '✏️', label: 'Type Freely' },
                  { id: 'image', icon: '📷', label: 'Upload Photo' },
                ].map(tab => (
                  <button key={tab.id} className={`mp-tab ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => { setActiveTab(tab.id); setError(''); }}>
                    {tab.icon} {tab.label}
                  </button>
                ))}
              </div>

              {/* TAB: DROPDOWN */}
              {activeTab === 'dropdown' && (
                <div className="mp-tab-content">
                  <p className="mp-tab-hint">Select a recipe for each meal slot. Leave empty to skip.</p>
                  <div className="mp-weekly-grid">
                    {DAYS.map(day => (
                      <div key={day} className="mp-day-card">
                        <div className="mp-day-header">
                          <span className="mp-day-name">{day}</span>
                          <span className="mp-day-filled">
                            {Object.values(mealPlan[day]).filter(Boolean).length}/3
                          </span>
                        </div>
                        <div className="mp-meal-selects">
                          {MEALS.map(meal => (
                            <div key={meal} className="mp-select-wrap">
                              <span className="mp-meal-icon">{MEAL_ICONS[meal]}</span>
                              <select
                                className="mp-select"
                                value={mealPlan[day][meal]}
                                onChange={e => setMeal(day, meal, e.target.value)}
                              >
                                <option value="">{meal.charAt(0).toUpperCase() + meal.slice(1)}</option>
                                {SL_RECIPES.map((r, i) => <option key={i} value={r}>{r}</option>)}
                              </select>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                  {error && <div className="mp-error">⚠️ {error}</div>}
                  <button className="mp-generate-btn" onClick={buildGroceryFromDropdown}
                    disabled={loading || dropdownMealCount === 0}>
                    {loading
                      ? <><span className="mp-spinner" /> Generating...</>
                      : <>🛒 Generate Grocery List ({dropdownMealCount} meals)</>}
                  </button>
                </div>
              )}

              {/* TAB: FREE TEXT */}
              {activeTab === 'text' && (
                <div className="mp-tab-content">
                  <p className="mp-tab-hint">Type your meal plan naturally. Our AI will understand and extract the meals.</p>
                  <div className="mp-text-examples">
                    <span className="mp-example-label">💡 Examples:</span>
                    <span className="mp-example">"Monday breakfast: hoppers, lunch: rice and curry, dinner: kottu"</span>
                    <span className="mp-example">"This week I want chicken curry on Tuesday, fish curry Wednesday, dhal every day"</span>
                  </div>
                  <textarea
                    className="mp-textarea"
                    placeholder="Type your weekly meal plan here...&#10;&#10;e.g. Monday: Rice &amp; Curry for lunch, Hoppers for dinner&#10;Tuesday: Kottu Roti for dinner&#10;Wednesday breakfast: Kiribath..."
                    value={freeText}
                    onChange={e => setFreeText(e.target.value)}
                    rows={8}
                  />
                  {parsedPlan && (
                    <div className="mp-parsed-preview">
                      <div className="mp-parsed-title">✅ AI Parsed Your Plan:</div>
                      {Object.entries(parsedPlan).map(([day, meals]) => (
                        <div key={day} className="mp-parsed-row">
                          <span className="mp-parsed-day">{day}</span>
                          <span className="mp-parsed-meals">
                            {typeof meals === 'object'
                              ? Object.values(meals).filter(Boolean).join(' • ')
                              : meals}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                  {error && <div className="mp-error">⚠️ {error}</div>}
                  <button className="mp-generate-btn" onClick={parseTextPlan}
                    disabled={loading || !freeText.trim()}>
                    {loading
                      ? <><span className="mp-spinner" /> Parsing with AI...</>
                      : <>🤖 Parse & Generate Grocery List</>}
                  </button>
                </div>
              )}

              {/* TAB: IMAGE UPLOAD */}
              {activeTab === 'image' && (
                <div className="mp-tab-content">
                  <p className="mp-tab-hint">Upload a photo of your handwritten or printed meal plan.</p>
                  <div
                    className={`mp-image-drop ${planImagePreview ? 'has-image' : ''}`}
                    onDragOver={e => e.preventDefault()}
                    onDrop={e => { e.preventDefault(); onImageSelect(e.dataTransfer.files[0]); }}
                    onClick={() => fileRef.current?.click()}
                  >
                    <input ref={fileRef} type="file" accept="image/*" style={{ display: 'none' }}
                      onChange={e => onImageSelect(e.target.files[0])} />
                    {planImagePreview
                      ? <img src={planImagePreview} alt="Plan" className="mp-plan-preview" />
                      : (
                        <div className="mp-drop-placeholder">
                          <div className="mp-drop-icon">📷</div>
                          <p className="mp-drop-text">Drop photo of your meal plan here</p>
                          <p className="mp-drop-hint">or click to browse • JPG PNG GIF</p>
                          <p className="mp-drop-hint">Works with handwritten notes, whiteboard photos, printed schedules</p>
                        </div>
                      )
                    }
                  </div>
                  {planImagePreview && (
                    <button className="mp-clear-btn"
                      onClick={() => { setPlanImage(null); setPlanImagePreview(null); setParsedPlan(null); }}>
                      🗑️ Clear Image
                    </button>
                  )}
                  {parsedPlan && (
                    <div className="mp-parsed-preview">
                      <div className="mp-parsed-title">✅ AI Read Your Plan:</div>
                      {Object.entries(parsedPlan).map(([day, meals]) => (
                        <div key={day} className="mp-parsed-row">
                          <span className="mp-parsed-day">{day}</span>
                          <span className="mp-parsed-meals">
                            {typeof meals === 'object'
                              ? Object.values(meals).filter(Boolean).join(' • ')
                              : meals}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                  {error && <div className="mp-error">⚠️ {error}</div>}
                  <button className="mp-generate-btn" onClick={parseImagePlan}
                    disabled={loading || !planImage}>
                    {loading
                      ? <><span className="mp-spinner" /> Reading image with AI...</>
                      : <>📷 Read Plan & Generate Grocery List</>}
                  </button>
                </div>
              )}
            </div>
          </>
        )}

        {/* ══ GROCERY ══ */}
        {activeNav === 'grocery' && groceryList && (
          <>
            <div className="mp-hero mp-grocery-hero">
              <div className="mp-hero-text">
                <p className="mp-hero-tag">SmartKitchen • Grocery List</p>
                <h1 className="mp-hero-title">Your <span className="mp-hero-accent">Shopping List</span></h1>
                <p className="mp-hero-desc">
                  {groceryList.total_items} items • scaled for {numPeople} {numPeople === 1 ? 'person' : 'people'} • {groceryList.total_meals || '?'} meals
                </p>
              </div>
              <div className="mp-hero-visual">🛒</div>
            </div>

            <div className="mp-grocery-stats">
              {[
                { icon: '🧺', label: 'Total Items', value: groceryList.total_items },
                { icon: '👥', label: 'People', value: numPeople },
                { icon: '🍽️', label: 'Meals Planned', value: groceryList.total_meals || '—' },
                { icon: '📦', label: 'Categories', value: Object.keys(groceryList.categories || {}).length },
              ].map((s, i) => (
                <div key={i} className="mp-stat-card">
                  <span className="mp-stat-icon">{s.icon}</span>
                  <div>
                    <div className="mp-stat-value">{s.value}</div>
                    <div className="mp-stat-label">{s.label}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mp-grocery-grid" id="grocery-print-area">
              {Object.entries(groceryList.categories || {}).map(([cat, items]) => (
                items.length > 0 && (
                  <div key={cat} className="mp-grocery-card">
                    <h3 className="mp-grocery-cat-title">{cat}</h3>
                    <ul className="mp-grocery-list">
                      {items.map((item, i) => (
                        <li key={i} className="mp-grocery-item">
                          <div className="mp-grocery-check">
                            <input type="checkbox" id={`item-${cat}-${i}`} />
                            <label htmlFor={`item-${cat}-${i}`}>{item.name}</label>
                          </div>
                          <span className="mp-grocery-amount">{item.scaled_amount}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )
              ))}
            </div>

            <div className="mp-actions">
              <button className="mp-action-btn secondary" onClick={() => setActiveNav('planner')}>
                ← Edit Meal Plan
              </button>
              <button className="mp-action-btn primary" onClick={handlePrint}>
                🖨️ Print List
              </button>
              <button className="mp-action-btn success" onClick={() => {
                const text = Object.entries(groceryList.categories || {})
                  .flatMap(([cat, items]) => [`\n${cat}`, ...items.map(i => `  • ${i.name} — ${i.scaled_amount}`)])
                  .join('\n');
                const blob = new Blob([`GROCERY LIST (${numPeople} people)\n${text}`], { type: 'text/plain' });
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = 'grocery_list.txt';
                a.click();
              }}>
                ⬇️ Download
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}