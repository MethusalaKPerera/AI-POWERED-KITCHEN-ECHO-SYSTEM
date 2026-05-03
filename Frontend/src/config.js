
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
export const API_URL = `${BASE_URL}/api`;
export const HEALTH_URL = `${BASE_URL}/health`;
export default BASE_URL;
