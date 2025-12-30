import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Analyze ingredients using the backend API
 * @param {string[]} ingredients - Array of ingredient names
 * @param {string} mode - Analysis mode: 'BULK' or 'CUT'
 * @returns {Promise} API response with score and analysis
 */
export const analyzeIngredients = async (ingredients, mode = 'BULK') => {
    try {
        const response = await api.post('/scan', {
            ingredients,
            mode,
        });
        return response.data;
    } catch (error) {
        console.error('Error analyzing ingredients:', error);
        throw error;
    }
};

export default api;
