// API service for external loss dataset
import axiosClient from './axiosClient';

const externalLossAPI = {
  // Search external losses by ID
  search: async (id, limit = 1) => {
    const response = await axiosClient.get('/api/external-loss', {
      params: { id, limit }
    });
    return response.data;
  },

  // Get external loss details
  getDetails: async (extLossId) => {
    const response = await axiosClient.get(`/api/external-loss/${extLossId}/details`);
    return response.data;
  },

  // Trigger AI taxonomy
  triggerAITaxonomy: async (extLossId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/external-loss/${extLossId}/ai-taxonomy`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger AI root causes
  triggerAIRootCauses: async (extLossId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/external-loss/${extLossId}/ai-root-causes`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger AI enrichment
  triggerAIEnrichment: async (extLossId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/external-loss/${extLossId}/ai-enrichment`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger similar external losses
  triggerSimilarExternalLoss: async (extLossId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/external-loss/${extLossId}/similar-external-loss`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // List all external losses
  list: async (offset = 0, limit = 100) => {
    const response = await axiosClient.get('/api/external-loss/list', {
      params: { offset, limit }
    });
    return response.data;
  },

  // Search by taxonomy
  searchByTaxonomy: async (taxonomyToken, limit = 100) => {
    const response = await axiosClient.get(`/api/external-loss/taxonomy/${taxonomyToken}`, {
      params: { limit }
    });
    return response.data;
  }
};

export default externalLossAPI;