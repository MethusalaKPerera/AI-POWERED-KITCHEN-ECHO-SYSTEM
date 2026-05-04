import React, { useState, useEffect, useRef } from 'react';
import './CookingAssistant.css';
import LanguageSelector from '../../Components/LanguageSelector';

function CookingAssistant() {
  const [selectedImage, setSelectedImage]       = useState(null);
  const [previewUrl, setPreviewUrl]             = useState(null);
  const [ingredients, setIngredients]           = useState([]);
  const [recipes, setRecipes]                   = useState([]);
  const [allRecipes, setAllRecipes]             = useState([]);
  const [loading, setLoading]                   = useState(false);
  const [error, setError]                       = useState(null);
  const [selectedRecipe, setSelectedRecipe]     = useState(null);
  const [activeNav, setActiveNav]               = useState('detect');
  const [dragOver, setDragOver]                 = useState(false);
  const [manualInput, setManualInput]           = useState('');
  const [searchingRecipes, setSearchingRecipes] = useState(false);
  const [recommendation, setRecommendation]     = useState('');
  const [searchMethod, setSearchMethod]         = useState('');
  const [chatMessage, setChatMessage]           = useState('');
  const [chatLoading, setChatLoading]           = useState(false);
  const manualRef = useRef(null);

  useEffect(() => {
    const link = document.createElement('link');
    link.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap';
    link.rel  = 'stylesheet';
    document.head.appendChild(link);
  }, []);

  // ── Image ──────────────────────────────────────────────────────────────────
  const processFile = (file) => {
    setSelectedImage(file);
    setPreviewUrl(URL.createObjectURL(file));
    setError(null);
  };

  const analyzeImage = async () => {
    if (!selectedImage) { setError('Please select an image first!'); return; }
    setLoading(true); setError(null);
    try {
      const fd = new FormData();
      fd.append('image', selectedImage);
      const res  = await fetch('http://localhost:5000/api/cooking/analyze-image', { method: 'POST', body: fd });
      const data = await res.json();
      if (data.success) {
        const merged = mergeIngredients(ingredients, data.ingredients);
        setIngredients(merged);
        await triggerRecipeSearch(merged);
      } else setError(data.error || 'Failed to analyze image');
    } catch {
      setError('Error connecting to backend. Make sure Flask is running on port 5000!');
    } finally { setLoading(false); }
  };

  // ── Ingredients ────────────────────────────────────────────────────────────
  const mergeIngredients = (existing, newOnes) => {
    const combined = [...existing];
    newOnes.forEach(item => {
      if (!combined.includes(item.toLowerCase())) combined.push(item.toLowerCase());
    });
    return combined;
  };

  const addManualIngredient = () => {
    const raw = manualInput.trim().toLowerCase();
    if (!raw) return;
    const items   = raw.split(',').map(s => s.trim()).filter(s => s.length > 0);
    const updated = mergeIngredients(ingredients, items);
    setIngredients(updated);
    setManualInput('');
    manualRef.current?.focus();
  };

  const removeIngredient = (ing) => setIngredients(ingredients.filter(i => i !== ing));

  // ── Recipe Search ──────────────────────────────────────────────────────────
  const triggerRecipeSearch = async (list) => {
    if (!list || list.length === 0) return;
    setSearchingRecipes(true);
    setRecommendation('');
    try {
      const res  = await fetch('http://localhost:5000/api/cooking/search-recipes', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ ingredients: list }),
      });
      const data = await res.json();
      if (data.success) {
        const found = data.recipes || [];
        setRecipes(found);
        setAllRecipes(found);
        setRecommendation(data.recommendation || '');
        setSearchMethod(data.search_method || '');
        console.log('Search method:', data.search_method);
      }
    } catch (e) { console.error(e); }
    finally { setSearchingRecipes(false); }
  };

  const findRecipes = async () => {
    if (ingredients.length === 0) { setError('Add at least one ingredient first!'); return; }
    await triggerRecipeSearch(ingredients);
  };

  // ── Like / Reject ──────────────────────────────────────────────────────────
  const likeRecipe = async (recipe) => {
    try {
      await fetch('http://localhost:5000/api/cooking/like-recipe', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ id: recipe.id, name: recipe.name }),
      });
    } catch (e) { console.error(e); }
  };

  const rejectRecipe = async (recipe) => {
    try {
      await fetch('http://localhost:5000/api/cooking/reject-recipe', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ id: recipe.id, name: recipe.name }),
      });
    } catch (e) { console.error(e); }
    setRecipes(prev => prev.filter(r => r.id !== recipe.id));
    setAllRecipes(prev => prev.filter(r => r.id !== recipe.id));
    if (selectedRecipe?.id === recipe.id) setSelectedRecipe(null);
  };

  // ── Chat / AI Preferences ──────────────────────────────────────────────────
  const sendChat = async () => {
    if (!chatMessage.trim()) return;
    setChatLoading(true);

    const msg  = chatMessage.toLowerCase().trim();
    let base   = [...allRecipes];
    let note   = '';

    const MEAT = ['chicken','fish','prawn','beef','pork','mutton','lamb',
                  'tuna','sardine','shrimp','malu','crab','squid','duck'];

    if (msg.includes('vegetarian') || msg.includes('no meat') || msg.includes('veg')) {
      base = base.filter(r => !MEAT.some(m => r.name.toLowerCase().includes(m)));
      note = `Showing ${base.length} vegetarian recipes — meat dishes removed.`;
    }
    else if (msg.includes('easy') || msg.includes('simple')) {
      base = base.filter(r => r.difficulty?.toLowerCase() === 'easy');
      note = `Showing ${base.length} easy recipes.`;
    }
    else if (
      (msg.includes("don't") || msg.includes('no') || msg.includes('not') || msg.includes('less')) &&
      msg.includes('spicy')
    ) {
      base = base.filter(r => (r.spice_level || 3) <= 2);
      note = `Showing ${base.length} mild / low-spice recipes.`;
    }
    else if (msg.includes('quick') || msg.includes('fast') || msg.includes('30 min')) {
      base = base.filter(r => {
        const mins = parseInt(r.cooking_time || '60');
        return !isNaN(mins) && mins <= 30;
      });
      note = `Showing ${base.length} recipes under 30 minutes.`;
    }
    else if (msg.includes('hard') || msg.includes('difficult') || msg.includes('challenge')) {
      base = base.filter(r => r.difficulty?.toLowerCase() === 'hard');
      note = `Showing ${base.length} challenging recipes.`;
    }
    else if (msg.includes('dessert') || msg.includes('sweet')) {
      base = base.filter(r => r.category?.toLowerCase().includes('dessert'));
      note = `Showing ${base.length} dessert recipes.`;
    }
    else if (msg.includes('breakfast')) {
      base = base.filter(r => r.category?.toLowerCase().includes('breakfast'));
      note = `Showing ${base.length} breakfast recipes.`;
    }
    else if (msg.includes('reset') || msg.includes('show all') || msg.includes('clear filter')) {
      base = [...allRecipes];
      note = `Reset — showing all ${base.length} recipes.`;
    }
    else {
      // Try backend
      try {
        const res  = await fetch('http://localhost:5000/api/cooking/chat', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({ message: chatMessage, ingredients }),
        });
        const data = await res.json();
        if (data.success) {
          note = data.recommendation || '';
          if (data.results?.length > 0) {
            base = data.results;
            setAllRecipes(data.results);
          }
        }
      } catch {
        note = 'Try: "vegetarian", "easy", "no spicy", "quick", "dessert", or "reset"';
      }
    }

    setRecipes(base);
    setRecommendation(note);
    setChatMessage('');
    setChatLoading(false);
  };

  // ── Helpers ────────────────────────────────────────────────────────────────
  const mc = (s) => s >= 80 ? '#10b981' : s >= 50 ? '#f59e0b' : '#6b7280';

  const di = (d) => {
    if (!d) return '';
    const l = d.toLowerCase();
    return l === 'easy' ? 'Easy' : l === 'hard' ? 'Hard' : 'Medium';
  };

  const parseInstructions = (instructions) => {
    if (!instructions) return [];
    if (Array.isArray(instructions)) return instructions;
    const steps = instructions
      .split(/\n+/)
      .map(s => s.replace(/^\d+\.\s*/, '').trim())
      .filter(s => s.length > 0);
    return steps.length > 0 ? steps : [instructions];
  };

  const methodBadge = () => {
    if (searchMethod === 'rag-sbert')        return { label: '🧠 Full RAG',  color: '#6366f1' };
    if (searchMethod === 'sentence-bert')    return { label: '🤖 SBERT',     color: '#0ea5e9' };
    if (searchMethod === 'keyword-fallback') return { label: '🔑 Keyword',   color: '#6b7280' };
    return null;
  };

  // ── JSX ────────────────────────────────────────────────────────────────────
  return (
    <div className="ca-root">

      {/* ── Sidebar ── */}
      <aside className="ca-sidebar">
        <div className="ca-logo">
          <span className="ca-logo-icon">🍛</span>
          <div>
            <h2 className="ca-logo-title">AI Kitchen</h2>
            <span className="ca-logo-sub">Sri Lankan Cuisine</span>
          </div>
        </div>

        <nav className="ca-nav">
          {[
            { id: 'detect',  icon: '📸', label: 'Detect Ingredients' },
            { id: 'meal',    icon: '📅', label: 'Meal Planner' },
            { id: 'grocery', icon: '🛒', label: 'Grocery List' },
          ].map(item => (
            <button
              key={item.id}
              className={`ca-nav-item ${activeNav === item.id ? 'active' : ''}`}
              onClick={() => {
                setActiveNav(item.id);
                if (item.id === 'meal') window.location.href = '/meal-planner';
              }}
            >
              <span className="ca-nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <LanguageSelector />

        <div className="ca-sidebar-footer">
          <div className="ca-badge">
            <span className="ca-flag">🇱🇰</span>
            <div>
              <div className="ca-badge-title">Authentic Sri Lankan</div>
              <div className="ca-badge-sub">Traditional Recipes</div>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="ca-main">

        {/* Hero */}
        <div className="ca-hero">
          <div className="ca-hero-text">
            <p className="ca-hero-tag">SmartKitchen • Cooking Assistant</p>
            <h1 className="ca-hero-title">
              Discover recipes from <span className="ca-hero-accent">your ingredients</span>
            </h1>
            <p className="ca-hero-desc">
              Upload a photo or type ingredients manually, then get matched authentic Sri Lankan recipes instantly.
            </p>
          </div>
          <div className="ca-hero-visual">🍲</div>
        </div>

        {/* Stats */}
        <div className="ca-stats">
          {[
            { icon: '🥬', label: 'Ingredients',  value: ingredients.length || '—' },
            { icon: '📖', label: 'Recipes Found', value: recipes.length || '—' },
            { icon: '🎯', label: 'Best Match',    value: recipes.length ? `${Math.max(...recipes.map(r => r.match_score || 0))}%` : '—' },
            { icon: '🍽️', label: 'Cuisine',       value: 'Sri Lankan' },
          ].map((s, i) => (
            <div className="ca-stat-card" key={i}>
              <span className="ca-stat-icon">{s.icon}</span>
              <div>
                <div className="ca-stat-value">{s.value}</div>
                <div className="ca-stat-label">{s.label}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Image upload */}
        <div className="ca-section">
          <div className="ca-section-header">
            <div>
              <h2 className="ca-section-title">📸 Analyze Your Ingredients</h2>
              <p className="ca-section-sub">Upload a photo or add ingredients manually below</p>
            </div>
          </div>
          <div className="ca-upload-row">
            <div
              className={`ca-dropzone ${dragOver ? 'drag-over' : ''} ${previewUrl ? 'has-image' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault(); setDragOver(false);
                const f = e.dataTransfer.files[0];
                if (f && f.type.startsWith('image/')) processFile(f);
              }}
            >
              <input
                type="file"
                id="img-upload"
                accept="image/*"
                onChange={(e) => { const f = e.target.files[0]; if (f) processFile(f); }}
                style={{ display: 'none' }}
              />
              <label htmlFor="img-upload" className="ca-dropzone-label">
                {previewUrl
                  ? <img src={previewUrl} alt="Preview" className="ca-preview-img" />
                  : (
                    <div className="ca-dropzone-placeholder">
                      <div className="ca-dropzone-icon">📷</div>
                      <p className="ca-dropzone-text">Drop your image here</p>
                      <p className="ca-dropzone-hint">or click to browse • JPG PNG GIF</p>
                    </div>
                  )
                }
              </label>
            </div>

            <div className="ca-upload-actions">
              <div className="ca-action-card">
                <div className="ca-action-icon">🤖</div>
                <h3>AI Detection</h3>
                <p>AI identifies ingredients from your image with high accuracy</p>
              </div>
              <div className="ca-action-card">
                <div className="ca-action-icon">🍜</div>
                <h3>Recipe Matching</h3>
                <p>Matched to authentic Sri Lankan recipes from our database</p>
              </div>
              <button
                className="ca-analyze-btn"
                onClick={analyzeImage}
                disabled={!selectedImage || loading}
              >
                {loading
                  ? <><span className="ca-spinner"></span> Analyzing...</>
                  : <>📸 Detect from Image</>
                }
              </button>
              {previewUrl && (
                <button
                  className="ca-clear-btn"
                  onClick={() => { setSelectedImage(null); setPreviewUrl(null); }}
                >
                  🗑️ Clear Image
                </button>
              )}
            </div>
          </div>
          {error && <div className="ca-error">⚠️ {error}</div>}
        </div>

        {/* Manual ingredient input */}
        <div className="ca-section">
          <div className="ca-section-header">
            <div>
              <h2 className="ca-section-title">✏️ Add Ingredients Manually</h2>
              <p className="ca-section-sub">Type an ingredient and press Enter, or separate with commas</p>
            </div>
          </div>

          <div className="ca-manual-row">
            <div className="ca-manual-input-wrap">
              <span className="ca-manual-icon">🥄</span>
              <input
                ref={manualRef}
                className="ca-manual-input"
                type="text"
                placeholder="e.g. onion, garlic, coconut milk, curry leaves"
                value={manualInput}
                onChange={(e) => setManualInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') addManualIngredient(); }}
              />
              <button
                className="ca-manual-add-btn"
                onClick={addManualIngredient}
                disabled={!manualInput.trim()}
              >
                + Add
              </button>
            </div>
            <p className="ca-manual-hint">💡 Tip: Add multiple at once — "onion, garlic, tomato"</p>
          </div>

          {ingredients.length > 0 && (
            <div className="ca-ing-section">
              <div className="ca-ing-section-header">
                <span className="ca-ing-section-title">Your Ingredients</span>
                <span className="ca-count-badge">{ingredients.length} total</span>
                <button
                  className="ca-clear-all-btn"
                  onClick={() => {
                    setIngredients([]);
                    setRecipes([]);
                    setAllRecipes([]);
                    setRecommendation('');
                  }}
                >
                  🗑️ Clear All
                </button>
              </div>
              <div className="ca-ingredients-grid">
                {ingredients.map((ing, i) => (
                  <div
                    key={i}
                    className="ca-ing-chip removable"
                    style={{ animationDelay: `${i * 0.04}s` }}
                  >
                    <span className="ca-ing-dot"></span>
                    <span className="ca-ing-name">{ing}</span>
                    <button
                      className="ca-ing-remove"
                      onClick={() => removeIngredient(ing)}
                      title="Remove"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {ingredients.length > 0 && (
            <button
              className="ca-find-btn"
              onClick={findRecipes}
              disabled={searchingRecipes}
            >
              {searchingRecipes
                ? <><span className="ca-spinner"></span> Finding Recipes...</>
                : <>🔍 Find Recipes for {ingredients.length} Ingredient{ingredients.length > 1 ? 's' : ''}</>
              }
            </button>
          )}
        </div>

        {/* AI Recommendation Box */}
        {recommendation && (
          <div className="ca-section ca-fade-in" style={{ borderLeft: '4px solid #6366f1' }}>
            <div className="ca-section-header">
              <div>
                <h2 className="ca-section-title">🧠 AI Recommendation</h2>
                {methodBadge() && (
                  <span style={{
                    background:    methodBadge().color,
                    color:         'white',
                    fontSize:      '11px',
                    fontWeight:    600,
                    padding:       '3px 10px',
                    borderRadius:  '100px',
                    marginTop:     '6px',
                    display:       'inline-block',
                  }}>
                    {methodBadge().label}
                  </span>
                )}
              </div>
            </div>
            <p style={{ fontSize: '14px', color: '#374151', lineHeight: 1.7, whiteSpace: 'pre-line' }}>
              {recommendation}
            </p>
          </div>
        )}

        {/* Ask the AI Chef */}
        {recipes.length > 0 && (
          <div className="ca-section">
            <div className="ca-section-header">
              <div>
                <h2 className="ca-section-title">💬 Ask the AI Chef</h2>
                <p className="ca-section-sub">
                  Try: "vegetarian" • "easy" • "no spicy" • "quick" • "dessert" • "reset"
                </p>
              </div>
            </div>
            <div className="ca-manual-input-wrap">
              <span className="ca-manual-icon">💬</span>
              <input
                className="ca-manual-input"
                type="text"
                placeholder="e.g. vegetarian, easy, no spicy, quick, dessert"
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') sendChat(); }}
              />
              <button
                className="ca-manual-add-btn"
                onClick={sendChat}
                disabled={!chatMessage.trim() || chatLoading}
              >
                {chatLoading ? '...' : 'Ask'}
              </button>
            </div>
          </div>
        )}

        {/* Recipe cards */}
        {recipes.length > 0 && (
          <div className="ca-section ca-fade-in">
            <div className="ca-section-header">
              <h2 className="ca-section-title">🍽️ Recipe Suggestions</h2>
              <span className="ca-count-badge">{recipes.length} recipes</span>
            </div>
            <div className="ca-recipes-grid">
              {recipes.map((recipe, i) => (
                <div
                  key={recipe.id || i}
                  className="ca-recipe-card"
                  style={{ animationDelay: `${i * 0.07}s` }}
                >
                  <div className="ca-recipe-top">
                    <span
                      className="ca-match-pill"
                      style={{ background: mc(recipe.match_score) }}
                    >
                      {recipe.match_score}% Match
                    </span>
                    <span className="ca-cuisine-tag">
                      {recipe.category || recipe.cuisine || 'Sri Lankan'}
                    </span>
                  </div>

                  <h3 className="ca-recipe-name">{recipe.name}</h3>

                  <div className="ca-recipe-meta">
                    <span className="ca-meta-item">⏱️ {recipe.cooking_time || `${recipe.cook_time_mins || 30} mins`}</span>
                    <span className="ca-meta-item">📊 {di(recipe.difficulty)}</span>
                    {recipe.region && <span className="ca-meta-item">📍 {recipe.region}</span>}
                  </div>

                  {recipe.missing_ingredients?.length > 0 && (
                    <div className="ca-missing-block">
                      <span className="ca-missing-label">🛒 Need: </span>
                      <span className="ca-missing-text">
                        {recipe.missing_ingredients.slice(0, 3).join(', ')}
                        {recipe.missing_ingredients.length > 3
                          ? ` +${recipe.missing_ingredients.length - 3} more`
                          : ''}
                      </span>
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
                    <button
                      className="ca-view-btn"
                      onClick={() => { setSelectedRecipe(recipe); likeRecipe(recipe); }}
                    >
                      View Recipe →
                    </button>
                    <button
                      onClick={() => rejectRecipe(recipe)}
                      title="Not interested — remove this"
                      style={{
                        padding:      '11px 14px',
                        background:   'transparent',
                        border:       '2px solid #fca5a5',
                        borderRadius: '12px',
                        cursor:       'pointer',
                        fontSize:     '16px',
                        color:        '#ef4444',
                        transition:   'all .2s',
                        flexShrink:   0,
                      }}
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty state */}
        {recipes.length === 0 && allRecipes.length > 0 && (
          <div className="ca-section ca-fade-in" style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
            <h3 style={{ color: '#374151', marginBottom: '8px' }}>No recipes match that filter</h3>
            <p style={{ color: '#6b7280', marginBottom: '20px' }}>Try a different filter or reset to see all recipes</p>
            <button
              className="ca-find-btn"
              style={{ maxWidth: '200px', margin: '0 auto' }}
              onClick={() => { setRecipes(allRecipes); setRecommendation(''); }}
            >
              Reset Filters
            </button>
          </div>
        )}

      </main>

      {/* ── Recipe Modal ── */}
      {selectedRecipe && (
        <div className="ca-modal-bg" onClick={() => setSelectedRecipe(null)}>
          <div className="ca-modal" onClick={(e) => e.stopPropagation()}>
            <button className="ca-modal-close" onClick={() => setSelectedRecipe(null)}>✕</button>

            <div className="ca-modal-top">
              <div>
                <p className="ca-modal-cuisine">
                  {selectedRecipe.cuisine || selectedRecipe.region || 'Sri Lankan'}
                </p>
                <h2 className="ca-modal-title">{selectedRecipe.name}</h2>
                <div className="ca-modal-badges">
                  <span className="ca-mbadge green">✅ {selectedRecipe.match_score}% Match</span>
                  <span className="ca-mbadge gray">
                    ⏱️ {selectedRecipe.cooking_time || `${selectedRecipe.cook_time_mins || 30} mins`}
                  </span>
                  <span className="ca-mbadge gray">📊 {selectedRecipe.difficulty}</span>
                  {selectedRecipe.spice_level && (
                    <span className="ca-mbadge orange">🌶️ Spice {selectedRecipe.spice_level}/5</span>
                  )}
                  {searchMethod === 'rag-sbert' && (
                    <span className="ca-mbadge" style={{ background: 'rgba(99,102,241,.3)', color: '#c7d2fe' }}>
                      🧠 RAG
                    </span>
                  )}
                  {searchMethod === 'sentence-bert' && (
                    <span className="ca-mbadge" style={{ background: 'rgba(14,165,233,.3)', color: '#bae6fd' }}>
                      🤖 SBERT
                    </span>
                  )}
                </div>
              </div>
              <div className="ca-modal-emoji">🍛</div>
            </div>

            {selectedRecipe.description && (
              <p className="ca-modal-desc">{selectedRecipe.description}</p>
            )}
            {selectedRecipe.cultural_note && (
              <div className="ca-modal-note">
                <span>📜</span> {selectedRecipe.cultural_note}
              </div>
            )}

            <div className="ca-modal-body">

              {selectedRecipe.ingredients_used?.length > 0 && (
                <div className="ca-modal-sec">
                  <h3 className="ca-msec-title">✅ Ingredients You Have</h3>
                  <div className="ca-chips">
                    {selectedRecipe.ingredients_used.map((ing, i) => (
                      <span key={i} className="ca-chip green">{ing}</span>
                    ))}
                  </div>
                </div>
              )}

              {selectedRecipe.ingredients?.length > 0 && (
                <div className="ca-modal-sec">
                  <h3 className="ca-msec-title">📋 Full Ingredients List</h3>
                  <div className="ca-full-ingredients">
                    {selectedRecipe.ingredients.map((ing, i) => {
                      const name = typeof ing === 'object'
                        ? (typeof ing.name === 'object' ? ing.name?.english || '' : ing.name || '')
                        : ing;
                      const amount = typeof ing === 'object' ? ing.amount || '' : '';
                      return (
                        <div key={i} className="ca-full-ing-row">
                          <span className="ca-full-ing-name">{name}</span>
                          {amount && <span className="ca-full-ing-amount">{amount}</span>}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {selectedRecipe.missing_ingredients?.length > 0 && (
                <div className="ca-modal-sec">
                  <h3 className="ca-msec-title">🛒 You Will Also Need</h3>
                  <div className="ca-chips">
                    {selectedRecipe.missing_ingredients.map((ing, i) => (
                      <span key={i} className="ca-chip orange">{ing}</span>
                    ))}
                  </div>
                </div>
              )}

              {(selectedRecipe.instructions || selectedRecipe.method) && (
                <div className="ca-modal-sec">
                  <h3 className="ca-msec-title">📝 Step-by-Step Instructions</h3>
                  <div className="ca-steps">
                    {parseInstructions(selectedRecipe.instructions || selectedRecipe.method).map((step, i) => (
                      <div key={i} className="ca-step">
                        <div className="ca-step-num">{i + 1}</div>
                        <p className="ca-step-text">{step}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedRecipe.tips && (
                <div className="ca-modal-tip">
                  <span className="ca-tip-icon">💡</span>
                  <div>
                    <strong>Pro Tip</strong>
                    <p>{selectedRecipe.tips}</p>
                  </div>
                </div>
              )}

              {!selectedRecipe.instructions && !selectedRecipe.method && !selectedRecipe.ingredients?.length && (
                <div className="ca-modal-empty">
                  <p>🍳 Search online for <strong>"{selectedRecipe.name}"</strong> to find the complete recipe.</p>
                </div>
              )}

              {selectedRecipe.adaptive_ingredients?.length > 0 && (
                <div className="ca-modal-sec ca-rag-section">
                  <h3 className="ca-msec-title">🔄 Adaptive Ingredients</h3>
                  <div className="ca-subs-grid">
                    {selectedRecipe.adaptive_ingredients.map((sub, i) => (
                      <div key={i} className="ca-sub-card">
                        <div className="ca-sub-original">❌ {sub.original}</div>
                        <div className="ca-sub-arrow">→</div>
                        <div className="ca-sub-replacement">✅ {sub.substitute}</div>
                        {sub.notes && <div className="ca-sub-notes">{sub.notes}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default CookingAssistant;