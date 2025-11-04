// API service for controls dataset
import axiosClient from './axiosClient';

const controlsAPI = {
  // Search controls by ID
  search: async (id, limit = 100) => {
    const response = await axiosClient.get('/api/controls', {
      params: { id, limit }
    });
    return response.data;
  },

  // Get control details
  getDetails: async (controlId) => {
    const response = await axiosClient.get(`/api/controls/${controlId}/details`);
    return response.data;
  },

  // Trigger AI taxonomy
  triggerAITaxonomy: async (controlId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/controls/${controlId}/ai-taxonomy`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger AI root causes
  triggerAIRootCauses: async (controlId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/controls/${controlId}/ai-root-causes`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger AI enrichment
  triggerAIEnrichment: async (controlId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/controls/${controlId}/ai-enrichment`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger similar controls
  triggerSimilarControls: async (controlId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/controls/${controlId}/similar-controls`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // List all controls
  list: async (offset = 0, limit = 100) => {
    const response = await axiosClient.get('/api/controls/list', {
      params: { offset, limit }
    });
    return response.data;
  },

  // Search by taxonomy
  searchByTaxonomy: async (taxonomyToken, limit = 100) => {
    const response = await axiosClient.get(`/api/controls/taxonomy/${taxonomyToken}`, {
      params: { limit }
    });
    return response.data;
  }
};

export default controlsAPI;