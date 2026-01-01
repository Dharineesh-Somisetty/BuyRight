import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

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

/**
 * Fetch product details by barcode
 * @param {string} barcode - Product barcode
 * @returns {Promise} Product details including ingredients_text
 */
export const getProductByBarcode = async (barcode) => {
    try {
        const response = await api.get(`/product/${barcode}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching product by barcode:', error);
        throw error;
    }
};

export default api;
