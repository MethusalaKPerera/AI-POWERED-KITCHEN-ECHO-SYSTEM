import React, { useState, useRef } from 'react';
import './EnhancedCookingAssistant.css';
import api from './api';

const EnhancedCookingAssistant = () => {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [ingredients, setIngredients] = useState([]);
  const [manualIngredient, setManualIngredient] = useState('');
  const [recipes, setRecipes] = useState([]);
  const [partialMatches, setPartialMatches] = useState([]);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [language, setLanguage] = useState('english');
  const [loading, setLoading] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImage(file);
    setImagePreview(URL.createObjectURL(file));
    setError(null);
    setLoading(true);

    try {
      const data = await api.analyzeImageEnhanced(file);
      if (data.success) {
        setIngredients(data.ingredients || []);
      } else {
        setError(data.error || 'Image analysis failed');
      }
    } catch (err) {
      setError('Failed to connect to backend - is server running on port 5000?');
    }
    setLoading(false);
  };

  const addManualIngredient = () => {
    if (manualIngredient.trim()) {
      setIngredients([...ingredients, { name: manualIngredient.trim(), confidence: 1.0 }]);
      setManualIngredient('');
    }
  };

  const searchRecipes = async () => {
    if (ingredients.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const ingNames = ingredients.map(i => typeof i === 'string' ? i : i.name);
      const data = await api.searchRecipesEnhanced(ingNames);
      if (data.success) {
        setRecipes(data.recipes || []);
        setPartialMatches(data.partial_matches || []);
      }
    } catch (err) {
      setError('Recipe search failed - check backend connection');
    }
    setLoading(false);
  };

  const loadRecipeDetail = async (id) => {
    try {
      const data = await api.getRecipe(id);
      if (data.success) setSelectedRecipe(data.recipe);
    } catch { /* ignore */ }
  };

  const loadStats = async () => {
    try {
      const data = await api.getSystemStats();
      if (data.success) { setStats(data.stats); setShowStats(true); }
    } catch { /* ignore */ }
  };

  const removeIngredient = (idx) => {
    setIngredients(prev => prev.filter((_, i) => i !== idx));
  };

  const translateText = (text) => {
    // Placeholder for translation - would connect to backend translation API
    return text;
  };

  const spiceLevelLabel = (level) => ['None', 'Mild', 'Medium', 'Hot', 'Very Hot', 'Extreme'][level] || 'Medium';
  const spiceLevelEmoji = (level) => ['🫑', '🌶️', '🌶️🌶️', '🔥', '🔥🔥', '💀'][level] || '🌶️';

  return (
    <div className="eca-container">
      {/* Header */}
      <header className="eca-header">
        <div className="eca-header-content">
          <h1>🍛 AI-Powered Cooking Assistant</h1>
          <p className="eca-subtitle">Sri Lankan Recipe Intelligence · Computer Vision + RAG</p>
          <div className="eca-header-actions">
            <div className="eca-lang-switch">
              {['english', 'sinhala', 'tamil'].map(lang => (
                <button key={lang} className={`eca-lang-btn ${language === lang ? 'active' : ''}`} onClick={() => setLanguage(lang)}>
                  {lang === 'english' ? '🇬🇧 English' : lang === 'sinhala' ? '🇱🇰 සිංහල' : '🇱🇰 தமிழ்'}
                </button>
              ))}
            </div>
            <button className="eca-stats-btn" onClick={loadStats}>📊 System Stats</button>
          </div>
        </div>
      </header>

      <main className="eca-main">
        {/* Upload Section */}
        <section className="eca-upload-section">
          <div className="eca-upload-card" onClick={() => fileInputRef.current?.click()}>
            {imagePreview ? (
              <img src={imagePreview} alt="Uploaded" className="eca-preview-img" />
            ) : (
              <div className="eca-upload-placeholder">
                <span className="eca-upload-icon">📷</span>
                <p>Upload Ingredient Photo</p>
                <small>PNG, JPG, JPEG · AI-Powered Detection</small>
              </div>
            )}
            <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageUpload} hidden />
          </div>
        </section>

        {/* Error Display */}
        {error && <div className="eca-error">⚠️ {error}</div>}

        {/* Loading */}
        {loading && <div className="eca-loading"><div className="eca-spinner"></div><p>Processing with AI...</p></div>}

        {/* Manual Ingredient Input */}
        <section className="eca-manual-input">
          <div className="eca-input-group">
            <input
              type="text"
              value={manualIngredient}
              onChange={(e) => setManualIngredient(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addManualIngredient()}
              placeholder="Add ingredient manually (e.g., 'rice', 'chicken')"
              className="eca-text-input"
            />
            <button onClick={addManualIngredient} className="eca-add-btn">+ Add</button>
          </div>
        </section>

        {/* Detected Ingredients */}
        {ingredients.length > 0 && (
          <section className="eca-ingredients-section">
            <h2>🥬 Your Ingredients ({ingredients.length})</h2>
            <div className="eca-ingredients-grid">
              {ingredients.map((ing, idx) => {
                const name = typeof ing === 'string' ? ing : ing.name;
                const conf = typeof ing === 'object' ? ing.confidence : null;
                return (
                  <div key={idx} className={`eca-ingredient-chip ${conf && conf > 0.8 ? 'high-conf' : 'low-conf'}`}>
                    <span className="eca-ing-name">{name}</span>
                    {conf && <span className="eca-confidence">{Math.round(conf * 100)}%</span>}
                    <button className="eca-remove-btn" onClick={() => removeIngredient(idx)}>×</button>
                  </div>
                );
              })}
            </div>
            <button className="eca-search-btn" onClick={searchRecipes} disabled={loading}>
              🔍 Find Recipes ({ingredients.length} ingredients)
            </button>
          </section>
        )}

        {/* Recipe Results */}
        {recipes.length > 0 && (
          <section className="eca-recipes-section">
            <h2>🍽️ Perfect Matches ({recipes.length})</h2>
            <div className="eca-recipes-grid">
              {recipes.map((recipe, idx) => (
                <div key={idx} className="eca-recipe-card" onClick={() => loadRecipeDetail(recipe.id)}>
                  <div className="eca-recipe-header">
                    <h3>{recipe.names?.english || recipe.name}</h3>
                    <div className="eca-match-badge" style={{
                      background: recipe.match_score >= 80 ? '#10B981' : recipe.match_score >= 50 ? '#F59E0B' : '#EF4444'
                    }}>{recipe.match_score}%</div>
                  </div>
                  <div className="eca-recipe-meta">
                    <span className="eca-meta-tag">{recipe.category}</span>
                    <span className="eca-meta-tag">{recipe.difficulty}</span>
                    <span className="eca-meta-tag">{spiceLevelEmoji(recipe.spice_level)} {spiceLevelLabel(recipe.spice_level)}</span>
                    {recipe.is_authentic && <span className="eca-auth-badge">✅ Authentic</span>}
                  </div>
                  <div className="eca-recipe-ingredients">
                    <small><strong>✓ Matched:</strong> {recipe.matched_ingredients?.join(', ')}</small>
                    {recipe.missing_ingredients?.length > 0 && (
                      <small className="eca-missing"><strong>✗ Missing:</strong> {recipe.missing_ingredients?.slice(0, 3).join(', ')}</small>
                    )}
                  </div>
                  {recipe.region && <div className="eca-region-tag">📍 {recipe.region}</div>}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Partial Matches */}
        {partialMatches.length > 0 && (
          <section className="eca-partial-section">
            <h2>🛒 Close Matches - Just Need a Few More Ingredients!</h2>
            <div className="eca-recipes-grid">
              {partialMatches.map((recipe, idx) => (
                <div key={idx} className="eca-recipe-card partial" onClick={() => loadRecipeDetail(recipe.id)}>
                  <h3>{recipe.names?.english || recipe.name}</h3>
                  <div className="eca-buy-more">
                    <strong>Shopping List:</strong> {recipe.buy_more?.join(', ')}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Recipe Detail Modal */}
        {selectedRecipe && (
          <div className="eca-modal-overlay" onClick={() => setSelectedRecipe(null)}>
            <div className="eca-modal" onClick={e => e.stopPropagation()}>
              <button className="eca-modal-close" onClick={() => setSelectedRecipe(null)}>×</button>

              <div className="eca-recipe-detail-header">
                <h2>{selectedRecipe.names?.[language] || selectedRecipe.names?.english || selectedRecipe.name}</h2>
                {language !== 'english' && selectedRecipe.names?.english && (
                  <p className="eca-alt-name">{selectedRecipe.names.english}</p>
                )}
              </div>

              <div className="eca-recipe-detail-meta">
                <span>⏱️ Prep: {selectedRecipe.prep_time_mins}min</span>
                <span>🔥 Cook: {selectedRecipe.cook_time_mins}min</span>
                <span>👥 Serves: {selectedRecipe.servings}</span>
                <span>📍 {selectedRecipe.region}</span>
                <span>{spiceLevelEmoji(selectedRecipe.spice_level)} {spiceLevelLabel(selectedRecipe.spice_level)}</span>
              </div>

              <h3>📝 Ingredients</h3>
              <ul className="eca-detail-ingredients">
                {selectedRecipe.ingredients?.map((ing, i) => (
                  <li key={i}>{ing.name} — {ing.amount}</li>
                ))}
              </ul>

              <h3>👨‍🍳 Cooking Method</h3>
              <pre className="eca-method">{selectedRecipe.method}</pre>

              {selectedRecipe.tips && (
                <>
                  <h3>💡 Pro Tips</h3>
                  <p className="eca-tips">{selectedRecipe.tips}</p>
                </>
              )}

              {selectedRecipe.cultural_note && (
                <>
                  <h3>🏛️ Cultural Significance</h3>
                  <p className="eca-cultural">{selectedRecipe.cultural_note}</p>
                </>
              )}
            </div>
          </div>
        )}

        {/* ML Stats Modal */}
        {showStats && stats && (
          <div className="eca-modal-overlay" onClick={() => setShowStats(false)}>
            <div className="eca-modal stats-modal" onClick={e => e.stopPropagation()}>
              <button className="eca-modal-close" onClick={() => setShowStats(false)}>×</button>
              <h2>📊 AI System Performance</h2>
              <div className="eca-stats-grid">
                <div className="eca-stat-card"><span className="eca-stat-value">{stats.total_recipes}</span><span className="eca-stat-label">Recipes</span></div>
                <div className="eca-stat-card"><span className="eca-stat-value">{stats.classification_accuracy}%</span><span className="eca-stat-label">Classification</span></div>
                <div className="eca-stat-card"><span className="eca-stat-value">{stats.fuzzy_matching_accuracy}%</span><span className="eca-stat-label">Fuzzy Matching</span></div>
                <div className="eca-stat-card"><span className="eca-stat-value">{stats.food_waste_reduction}%</span><span className="eca-stat-label">Waste Reduction</span></div>
                <div className="eca-stat-card"><span className="eca-stat-value">{stats.cultural_authenticity_score}%</span><span className="eca-stat-label">Authenticity</span></div>
                <div className="eca-stat-card"><span className="eca-stat-value">{stats.model_name}</span><span className="eca-stat-label">AI Model</span></div>
                <div className="eca-stat-card"><span className="eca-stat-value">p={stats.p_value}</span><span className="eca-stat-label">Significance</span></div>
                <div className="eca-stat-card"><span className="eca-stat-value">d={stats.cohens_d}</span><span className="eca-stat-label">Effect Size</span></div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default EnhancedCookingAssistant;