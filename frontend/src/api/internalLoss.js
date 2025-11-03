// API service for internal loss dataset
import axiosClient from './axiosClient';

const internalLossAPI = {
  // Search internal losses by ID
  search: async (id, limit = 1) => {
    const response = await axiosClient.get('/api/internal-loss', {
      params: { id, limit }
    });
    return response.data;
  },

  // Get internal loss details
  getDetails: async (lossId) => {
    const response = await axiosClient.get(`/api/internal-loss/${lossId}/details`);
    return response.data;
  },

  // Trigger AI taxonomy
  triggerAITaxonomy: async (lossId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/internal-loss/${lossId}/ai-taxonomy`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger AI root causes
  triggerAIRootCauses: async (lossId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/internal-loss/${lossId}/ai-root-causes`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger AI enrichment
  triggerAIEnrichment: async (lossId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/internal-loss/${lossId}/ai-enrichment`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger similar internal losses
  triggerSimilarInternalLoss: async (lossId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/internal-loss/${lossId}/similar-internal-loss`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // List all internal losses
  list: async (offset = 0, limit = 100) => {
    const response = await axiosClient.get('/api/internal-loss/list', {
      params: { offset, limit }
    });
    return response.data;
  },

  // Search by taxonomy
  searchByTaxonomy: async (taxonomyToken, limit = 100) => {
    const response = await axiosClient.get(`/api/internal-loss/taxonomy/${taxonomyToken}`, {
      params: { limit }
    });
    return response.data;
  }
};

export default internalLossAPI;