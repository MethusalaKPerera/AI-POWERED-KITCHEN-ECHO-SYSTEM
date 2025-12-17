const API_BASE_URL = '/api';

// Helper function to handle API requests
const apiRequest = async (endpoint, method = 'GET', body = null, headers = {}) => {
  // Check for token
  const token = localStorage.getItem('token');
  const authHeader = token ? { 'Authorization': `Bearer ${token}` } : {};

  const config = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...authHeader,
      ...headers,
    },
    credentials: 'include', // Important for sending cookies and handling CORS
    mode: 'cors', // Enable CORS mode
  };

  if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || 'Something went wrong');
  }

  return data;
};

// Shopping API
export const shoppingApi = {
  // Search products
  search: async (query, filters = {}) => {
    // Ensure all parameters are properly encoded
    const params = new URLSearchParams();
    params.append('q', query || '');

    // Add all filter parameters
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value);
      }
    });

    return apiRequest(`/shopping/search?${params.toString()}`);
  },

  // Get product details
  getProduct: async (productId) => {
    return apiRequest(`/shopping/product/${productId}`);
  },

  // Get shopping history
  getHistory: async () => {
    return apiRequest('/shopping/history');
  },

  // Get recommendations
  getRecommendations: async () => {
    return apiRequest('/shopping/recommendations');
  },

  // Save search to history
  saveToHistory: async (searchData) => {
    return apiRequest('/shopping/history', 'POST', searchData);
  },
};

// Add authentication methods if needed
export const authApi = {
  login: async (credentials) => {
    return apiRequest('/auth/login', 'POST', credentials);
  },
  register: async (userData) => {
    return apiRequest('/auth/register', 'POST', userData);
  },
  getProfile: async (token) => {
    return apiRequest('/auth/me', 'GET', null, {
      Authorization: `Bearer ${token}`,
    });
  },
};

export default {
  shopping: shoppingApi,
  auth: authApi,
};
