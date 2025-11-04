// API service for issues dataset
import axiosClient from './axiosClient';

const issuesAPI = {
  // Search issues by ID
  search: async (id, limit = 100) => {
    const response = await axiosClient.get('/api/issues', {
      params: { id, limit }
    });
    return response.data;
  },

  // Get issue details
  getDetails: async (issueId) => {
    const response = await axiosClient.get(`/api/issues/${issueId}/details`);
    return response.data;
  },

  // Trigger AI taxonomy
  triggerAITaxonomy: async (issueId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/issues/${issueId}/ai-taxonomy`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger AI root causes
  triggerAIRootCauses: async (issueId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/issues/${issueId}/ai-root-causes`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger AI enrichment
  triggerAIEnrichment: async (issueId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/issues/${issueId}/ai-enrichment`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // Trigger similar issues
  triggerSimilarIssues: async (issueId, description = null, refresh = false) => {
    const response = await axiosClient.post(
      `/api/issues/${issueId}/similar-issues`,
      { description },
      { params: { refresh } }
    );
    return response.data;
  },

  // List all issues
  list: async (offset = 0, limit = 100) => {
    const response = await axiosClient.get('/api/issues/list', {
      params: { offset, limit }
    });
    return response.data;
  },

  // Search by taxonomy
  searchByTaxonomy: async (taxonomyToken, limit = 100) => {
    const response = await axiosClient.get(`/api/issues/taxonomy/${taxonomyToken}`, {
      params: { limit }
    });
    return response.data;
  }
};

export default issuesAPI;