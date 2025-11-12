import React, { useState } from 'react';
import './CookingAssistant.css';

function CookingAssistant() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [ingredients, setIngredients] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
      setIngredients([]);
      setRecipes([]);
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) {
      setError("Please select an image first!");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("image", selectedImage);

      const response = await fetch("http://localhost:5000/api/cooking/analyze-image", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setIngredients(data.ingredients);
        searchRecipes(data.ingredients);
      } else {
        setError(data.error || "Failed to analyze image");
      }
    } catch (err) {
      setError("Error connecting to backend. Make sure Flask server is running on port 5000!");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const searchRecipes = async (ingredientList) => {
    try {
      const response = await fetch("http://localhost:5000/api/cooking/search-recipes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ingredients: ingredientList,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setRecipes(data.recipes);
      }
    } catch (err) {
      console.error("Error fetching recipes:", err);
    }
  };

  return (
    <div className="cooking-assistant-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-icon">🍛</div>
          <h2>AI Kitchen</h2>
          <p className="tagline">Sri Lankan Cuisine</p>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-item active">
            <span className="nav-icon">📸</span>
            <span>Detect Ingredients</span>
          </div>
          <div className="nav-item" onClick={() => window.location.href = '/meal-planner'}>
            <span className="nav-icon">📅</span>
            <span>Meal Planner</span>
          </div>
          <div className="nav-item">
            <span className="nav-icon">🛒</span>
            <span>Grocery List</span>
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
      <main className="cooking-assistant-page">
        <section className="section">
          <h2>🍳 AI Cooking Assistant</h2>
          <p className="subtitle">
            Upload an image of your ingredients, and our AI will identify them and suggest delicious recipes!
          </p>

          <div className="upload-container">
            <div className="upload-box">
              <input
                type="file"
                id="image-upload"
                accept="image/*"
                onChange={handleImageChange}
                style={{ display: "none" }}
              />
              <label htmlFor="image-upload" className="upload-label">
                {previewUrl ? (
                  <img src={previewUrl} alt="Preview" className="preview-image" />
                ) : (
                  <div className="upload-placeholder">
                    <span className="upload-icon">📷</span>
                    <p>Click to upload ingredient image</p>
                    <small>Supports: JPG, PNG, GIF</small>
                  </div>
                )}
              </label>
            </div>

            <button
              className="btn primary analyze-btn"
              onClick={analyzeImage}
              disabled={!selectedImage || loading}
            >
              {loading ? "🔍 Analyzing..." : "🚀 Analyze Ingredients"}
            </button>
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          {ingredients.length > 0 && (
            <div className="results-section">
              <h3>✅ Detected Ingredients:</h3>
              <div className="ingredients-list">
                {ingredients.map((ingredient, index) => (
                  <span key={index} className="ingredient-tag">
                    {ingredient}
                  </span>
                ))}
              </div>
            </div>
          )}

          {recipes.length > 0 && (
            <div className="results-section">
              <h3>🍽️ Recipe Suggestions:</h3>
              <div className="recipes-grid">
                {recipes.map((recipe) => (
                  <div key={recipe.id} className="recipe-card">
                    <div className="recipe-header">
                      <h4>{recipe.name}</h4>
                      <span className="match-score">{recipe.match_score}% Match</span>
                    </div>
                    <div className="recipe-details">
                      <p><strong>Cuisine:</strong> {recipe.cuisine}</p>
                      <p><strong>Time:</strong> {recipe.cooking_time}</p>
                      <p><strong>Difficulty:</strong> {recipe.difficulty}</p>
                      {recipe.missing_ingredients && recipe.missing_ingredients.length > 0 && (
                        <p className="missing">
                          <strong>You'll need:</strong> {recipe.missing_ingredients.join(", ")}
                        </p>
                      )}
                    </div>
                    <button className="btn secondary">View Recipe</button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default CookingAssistant;