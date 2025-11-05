// API service for internal loss dataset
import axiosClient from './axiosClient';

const triggerIssueTaxonomy = async (eventId, refresh = false) => {
  const response = await axiosClient.post(
    `/api/internal-loss/${eventId}/issue-taxonomy`,
    null,
    { params: { refresh } }
  );
  return response.data;
};

const triggerRootCause = async (eventId, refresh = false) => {
  const response = await axiosClient.post(
    `/api/internal-loss/${eventId}/root-cause`,
    null,
    { params: { refresh } }
  );
  return response.data;
};

const triggerEnrichment = async (eventId, refresh = false) => {
  const response = await axiosClient.post(
    `/api/internal-loss/${eventId}/enrichment`,
    null,
    { params: { refresh } }
  );
  return response.data;
};

const internalLossAPI = {
  search: async (id, limit = 100) => {
    const response = await axiosClient.get('/api/internal-loss', {
      params: { id, limit }
    });
    return response.data;
  },

  getDetails: async (eventId) => {
    const response = await axiosClient.get(`/api/internal-loss/${eventId}/details`);
    return response.data;
  },

  list: async (offset = 0, limit = 100) => {
    const response = await axiosClient.get('/api/internal-loss/list', {
      params: { offset, limit }
    });
    return response.data;
  },

  aiTriggers: {
    issue_taxonomy: triggerIssueTaxonomy,
    root_cause: triggerRootCause,
    enrichment: triggerEnrichment
  },

  meta: {
    primaryFunction: 'issue_taxonomy',
    titleField: 'event_title',
    typeField: 'event_type',
    themeField: 'risk_theme',
    subthemeField: 'risk_subtheme',
    functionLabels: {
      issue_taxonomy: 'Loss Taxonomy',
      root_cause: 'Root Cause',
      enrichment: 'Enrichment'
    }
  }
};

export default internalLossAPI;
