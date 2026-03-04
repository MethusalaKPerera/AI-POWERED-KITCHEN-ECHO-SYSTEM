import React, { useState, useEffect } from 'react';
import api from './api';

function ConnectionTest() {
    const [status, setStatus] = useState({
        backend: 'checking...',
        message: '',
        blueprints: 0
    });
    const [ingredients, setIngredients] = useState('rice, chicken, curry leaves');
    const [recipes, setRecipes] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        testConnection();
        loadStats();
    }, []);

    const testConnection = async () => {
        try {
            const health = await api.checkHealth();
            setStatus({
                backend: '✅ Connected',
                message: health.service || 'Backend is running!',
                blueprints: health.blueprints_loaded || 0
            });
        } catch (error) {
            setStatus({
                backend: '❌ Disconnected',
                message: 'Start server: python server.py',
                blueprints: 0
            });
        }
    };

    const loadStats = async () => {
        try {
            const data = await api.getSystemStats();
            setStats(data);
        } catch (error) {
            console.log('Stats not available:', error);
        }
    };

    const searchRecipes = async () => {
        setLoading(true);
        try {
            const ingredientList = ingredients.split(',').map(i => i.trim());
            const result = await api.searchRecipesEnhanced(ingredientList);
            setRecipes(result.recipes || []);
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial', maxWidth: '1200px', margin: '0 auto' }}>
            <h1>🍳 AI Kitchen Assistant - Connection Test</h1>

            {/* Connection Status */}
            <div style={{
                padding: '15px',
                marginBottom: '20px',
                background: status.backend.includes('✅') ? '#d4edda' : '#f8d7da',
                border: '1px solid ' + (status.backend.includes('✅') ? '#c3e6cb' : '#f5c6cb'),
                borderRadius: '5px'
            }}>
                <strong>Backend Status:</strong> {status.backend}
                <br />
                <small>{status.message}</small>
                {status.blueprints > 0 && (
                    <>
                        <br />
                        <small>✓ {status.blueprints} route blueprints loaded</small>
                    </>
                )}
            </div>

            {/* System Stats */}
            {stats && (
                <div style={{
                    padding: '15px',
                    marginBottom: '20px',
                    background: '#e7f3ff',
                    border: '1px solid #b3d9ff',
                    borderRadius: '5px'
                }}>
                    <h3>📊 System Information</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
                        <div>
                            <strong>Total Recipes:</strong> {stats.total_recipes || 'N/A'}
                        </div>
                        <div>
                            <strong>Cuisines:</strong> {stats.unique_cuisines || 'N/A'}
                        </div>
                        <div>
                            <strong>Uptime:</strong> {stats.uptime_seconds ? `${Math.floor(stats.uptime_seconds)}s` : 'N/A'}
                        </div>
                    </div>
                </div>
            )}

            {/* Recipe Search */}
            <div style={{ marginBottom: '20px' }}>
                <h3>🔍 Search Recipes by Ingredients</h3>
                <input
                    type="text"
                    value={ingredients}
                    onChange={(e) => setIngredients(e.target.value)}
                    placeholder="Enter ingredients (comma-separated)"
                    style={{
                        width: 'calc(100% - 130px)',
                        padding: '10px',
                        fontSize: '16px',
                        marginRight: '10px'
                    }}
                />
                <button
                    onClick={searchRecipes}
                    disabled={loading}
                    style={{
                        padding: '10px 20px',
                        fontSize: '16px',
                        background: loading ? '#ccc' : '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: loading ? 'not-allowed' : 'pointer'
                    }}
                >
                    {loading ? 'Searching...' : 'Search'}
                </button>
            </div>

            {/* Results */}
            {recipes.length > 0 && (
                <div>
                    <h3>✅ Found {recipes.length} Recipes:</h3>
                    <div style={{ display: 'grid', gap: '15px' }}>
                        {recipes.map((recipe, idx) => (
                            <div key={idx} style={{
                                padding: '15px',
                                border: '1px solid #ddd',
                                borderRadius: '5px',
                                background: '#f9f9f9'
                            }}>
                                <h4 style={{ margin: '0 0 10px 0' }}>{recipe.name}</h4>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '14px' }}>
                                    <div>
                                        <strong>Cuisine:</strong> {recipe.cuisine || 'N/A'}
                                    </div>
                                    <div>
                                        <strong>Confidence:</strong> {recipe.confidence_score ?
                                            `${(recipe.confidence_score * 100).toFixed(1)}%` : 'N/A'}
                                    </div>
                                    <div style={{ gridColumn: '1 / -1' }}>
                                        <strong>Ingredients:</strong> {
                                            recipe.ingredients?.slice(0, 5).join(', ') || 'N/A'
                                        }
                                        {recipe.ingredients?.length > 5 && ` (+${recipe.ingredients.length - 5} more)`}
                                    </div>
                                    {recipe.authenticity_badge && (
                                        <div style={{ gridColumn: '1 / -1' }}>
                                            <span style={{
                                                background: '#ffd700',
                                                padding: '2px 8px',
                                                borderRadius: '3px',
                                                fontSize: '12px'
                                            }}>
                                                {recipe.authenticity_badge}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {recipes.length === 0 && !loading && (
                <div style={{
                    padding: '20px',
                    textAlign: 'center',
                    color: '#666',
                    border: '2px dashed #ddd',
                    borderRadius: '5px'
                }}>
                    Enter ingredients and click Search to test the API
                </div>
            )}
        </div>
    );
}

export default ConnectionTest;