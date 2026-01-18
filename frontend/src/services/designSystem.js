/**
 * Design System Service
 * 
 * Provides API functions for managing design systems including:
 * - CRUD operations
 * - Image upload
 * - AI analysis
 * - MCP configuration
 */
import api from '../lib/api';

const DESIGN_SYSTEM_BASE = '/design-system/systems';

/**
 * Design system status enum
 */
export const DesignSystemStatus = {
  DRAFT: 'draft',
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

/**
 * Get all design systems for the current user
 * @param {Object} params - Query parameters
 * @param {number} [params.page=1] - Page number (1-indexed)
 * @param {number} [params.pageSize=10] - Items per page
 * @returns {Promise<Object>} Paginated response with count, next, previous, and results
 */
export const getDesignSystems = async ({ page = 1, pageSize = 10 } = {}) => {
  const response = await api.get(`${DESIGN_SYSTEM_BASE}/`, {
    params: {
      page,
      page_size: pageSize
    }
  });
  // API returns paginated response: { count, next, previous, results }
  return response.data;
};

/**
 * Get a single design system by ID
 * @param {string} id - Design system UUID
 * @returns {Promise<Object>} Design system details
 */
export const getDesignSystem = async (id) => {
  const response = await api.get(`${DESIGN_SYSTEM_BASE}/${id}/`);
  return response.data;
};

/**
 * Create a new design system
 * @param {Object} data - Design system data
 * @param {string} data.name - Name of the design system
 * @param {string} [data.description] - Description of the design system
 * @returns {Promise<Object>} Created design system
 */
export const createDesignSystem = async (data) => {
  const response = await api.post(`${DESIGN_SYSTEM_BASE}/`, data);
  return response.data;
};

/**
 * Update a design system
 * @param {string} id - Design system UUID
 * @param {Object} data - Updated data
 * @returns {Promise<Object>} Updated design system
 */
export const updateDesignSystem = async (id, data) => {
  const response = await api.patch(`${DESIGN_SYSTEM_BASE}/${id}/`, data);
  return response.data;
};

/**
 * Delete a design system
 * @param {string} id - Design system UUID
 * @returns {Promise<void>}
 */
export const deleteDesignSystem = async (id) => {
  await api.delete(`${DESIGN_SYSTEM_BASE}/${id}/`);
};

/**
 * Upload images to a design system
 * @param {string} id - Design system UUID
 * @param {Array<Object>} images - Array of image objects
 * @param {string} images[].data - Base64 encoded image data
 * @param {string} images[].mime_type - MIME type of the image
 * @param {string} [images[].name] - Optional filename
 * @returns {Promise<Object>} Upload result
 */
export const uploadImages = async (id, images) => {
  const response = await api.post(`${DESIGN_SYSTEM_BASE}/${id}/upload_images/`, {
    images,
  });
  return response.data;
};

/**
 * Delete an image from a design system
 * @param {string} designSystemId - Design system UUID
 * @param {string} imageId - Image UUID
 * @returns {Promise<void>}
 */
export const deleteImage = async (designSystemId, imageId) => {
  await api.delete(`${DESIGN_SYSTEM_BASE}/${designSystemId}/images/${imageId}/`);
};

/**
 * Start AI analysis on a design system
 * @param {string} id - Design system UUID
 * @param {Object} [options] - Analysis options
 * @param {string} [options.provider] - LLM provider to use
 * @param {Array<Object>} [options.images] - Additional images to upload
 * @returns {Promise<Object>} Task info with task_id
 */
export const startAnalysis = async (id, options = {}) => {
  const response = await api.post(`${DESIGN_SYSTEM_BASE}/${id}/analyze/`, options);
  return response.data;
};

/**
 * Get analysis status for a design system
 * @param {string} id - Design system UUID
 * @returns {Promise<Object>} Analysis status
 */
export const getAnalysisStatus = async (id) => {
  const response = await api.get(`${DESIGN_SYSTEM_BASE}/${id}/analysis_status/`);
  return response.data;
};

/**
 * Poll for analysis completion
 * @param {string} id - Design system UUID
 * @param {Function} onProgress - Callback for progress updates
 * @param {number} [interval=2000] - Polling interval in ms
 * @returns {Promise<Object>} Final analysis result
 */
export const pollAnalysisStatus = (id, onProgress, interval = 2000) => {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const status = await getAnalysisStatus(id);
        
        if (onProgress) {
          onProgress(status);
        }
        
        if (status.status === 'completed') {
          resolve(status);
          return;
        }
        
        if (status.status === 'failed') {
          reject(new Error(status.error || 'Analysis failed'));
          return;
        }
        
        // Continue polling
        setTimeout(poll, interval);
      } catch (error) {
        reject(error);
      }
    };
    
    poll();
  });
};

/**
 * Toggle MCP exposure for a design system
 * @param {string} id - Design system UUID
 * @returns {Promise<Object>} Updated MCP status
 */
export const toggleMcp = async (id) => {
  const response = await api.post(`${DESIGN_SYSTEM_BASE}/${id}/toggle_mcp/`);
  return response.data;
};

/**
 * Get MCP configuration for a design system
 * @param {string} id - Design system UUID
 * @returns {Promise<Object>} MCP configuration
 */
export const getMcpConfig = async (id) => {
  const response = await api.get(`/design-system/mcp/${id}/config/`);
  return response.data;
};

/**
 * Get available LLM providers
 * @returns {Promise<Object>} Available providers info
 */
export const getProviders = async () => {
  const response = await api.get('/design-system/providers/');
  return response.data;
};

/**
 * Convert a File object to base64 image data
 * @param {File} file - File object to convert
 * @returns {Promise<Object>} Image data object
 */
export const fileToImageData = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = () => {
      const base64 = reader.result.split(',')[1];
      resolve({
        data: base64,
        mime_type: file.type || 'image/png',
        name: file.name,
      });
    };
    
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

/**
 * Convert multiple File objects to base64 image data
 * @param {FileList|Array<File>} files - Files to convert
 * @returns {Promise<Array<Object>>} Array of image data objects
 */
export const filesToImageData = async (files) => {
  const promises = Array.from(files).map(fileToImageData);
  return Promise.all(promises);
};

export default {
  getDesignSystems,
  getDesignSystem,
  createDesignSystem,
  updateDesignSystem,
  deleteDesignSystem,
  uploadImages,
  deleteImage,
  startAnalysis,
  getAnalysisStatus,
  pollAnalysisStatus,
  toggleMcp,
  getMcpConfig,
  getProviders,
  fileToImageData,
  filesToImageData,
  DesignSystemStatus,
};
