import api from '../lib/api';

/**
 * Service for managing user API keys
 */

/**
 * Fetch all API keys for the current user
 * @returns {Promise} Promise resolving to array of API keys
 */
export const fetchAPIKeys = async () => {
  const response = await api.get('/accounts/api-keys/');
  return response.data;
};

/**
 * Create a new API key
 * @param {Object} data - API key data
 * @param {string} data.name - Name/description for the key
 * @returns {Promise} Promise resolving to created API key (with full key value)
 */
export const createAPIKey = async (data) => {
  const response = await api.post('/accounts/api-keys/', data);
  return response.data;
};

/**
 * Delete an API key
 * @param {string} keyId - UUID of the API key to delete
 * @returns {Promise} Promise resolving to success message
 */
export const deleteAPIKey = async (keyId) => {
  const response = await api.delete(`/accounts/api-keys/${keyId}/`);
  return response.data;
};

/**
 * Update an API key (e.g., toggle active status or update name)
 * @param {string} keyId - UUID of the API key
 * @param {Object} data - Updated fields
 * @returns {Promise} Promise resolving to updated API key
 */
export const updateAPIKey = async (keyId, data) => {
  const response = await api.patch(`/accounts/api-keys/${keyId}/`, data);
  return response.data;
};
