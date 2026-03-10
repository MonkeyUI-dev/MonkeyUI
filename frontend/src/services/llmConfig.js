import api from '../lib/api';

/**
 * Service for managing user LLM provider configurations
 */

/**
 * Fetch all LLM configurations for the current user
 * @returns {Promise} Promise resolving to array of LLM configs
 */
export const fetchLLMConfigs = async () => {
  const response = await api.get('/accounts/llm-configs/');
  return response.data;
};

/**
 * Create a new LLM provider configuration
 * @param {Object} data - LLM config data
 * @param {string} data.provider - Provider name (gemini or openrouter)
 * @param {string} data.api_key - API key for the provider
 * @returns {Promise} Promise resolving to created config
 */
export const createLLMConfig = async (data) => {
  const response = await api.post('/accounts/llm-configs/', data);
  return response.data;
};

/**
 * Update an existing LLM provider configuration
 * @param {string} configId - UUID of the config to update
 * @param {Object} data - Updated fields
 * @returns {Promise} Promise resolving to updated config
 */
export const updateLLMConfig = async (configId, data) => {
  const response = await api.patch(`/accounts/llm-configs/${configId}/`, data);
  return response.data;
};

/**
 * Delete an LLM provider configuration
 * @param {string} configId - UUID of the config to delete
 * @returns {Promise} Promise resolving to success message
 */
export const deleteLLMConfig = async (configId) => {
  const response = await api.delete(`/accounts/llm-configs/${configId}/`);
  return response.data;
};

/**
 * Check if the user has a default LLM provider configured
 * @returns {Promise} Promise resolving to { ready: boolean, default_provider: string|null }
 */
export const checkLLMReadiness = async () => {
  const response = await api.get('/accounts/llm-configs/readiness/');
  return response.data;
};
