// Dynamic API Configuration
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
const API_BASE = `${BASE_URL}/api`;

export const api = {
    // Health check
    checkHealth: async () => {
        const response = await fetch(`${BASE_URL}/health`);
        return response.json();
    },

    // System stats (enhanced routes)
    getSystemStats: async () => {
        const response = await fetch(`${API_BASE}/system-stats`);
        return response.json();
    },

    // FIXED: Image analysis (enhanced)
    analyzeImageEnhanced: async (imageFile) => {
        const formData = new FormData();
        formData.append('image', imageFile);
        const response = await fetch(`${API_BASE}/analyze-image-enhanced`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    },

    // FIXED: Search recipes (enhanced)
    searchRecipesEnhanced: async (ingredients) => {
        const response = await fetch(`${API_BASE}/search-recipes-enhanced`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ingredients })
        });
        return response.json();
    },

    // Get recipe details
    getRecipe: async (recipeId) => {
        const response = await fetch(`${API_BASE}/recipe/${recipeId}`);
        return response.json();
    },

    // Generate meal plan
    generateMealPlan: async (numPeople, preferences) => {
        const response = await fetch(`${API_BASE}/generate-meal-plan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ num_people: numPeople, preferences })
        });
        return response.json();
    },

    // Generate grocery list
    generateGroceryList: async (mealPlan, numPeople) => {
        const response = await fetch(`${API_BASE}/generate-grocery-list`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ meal_plan: mealPlan, num_people: numPeople })
        });
        return response.json();
    }
};

export default api;