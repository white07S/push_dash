// API service for controls dataset
import axiosClient from './axiosClient';

const triggerControlsTaxonomy = async (controlId, sessionId, userId, refresh = false) => {
  const response = await axiosClient.post(
    `/api/controls/${controlId}/controls-taxonomy`,
    { session_id: sessionId, user_id: userId },
    { params: { refresh } }
  );
  return response.data;
};

const triggerRootCause = async (controlId, sessionId, userId, refresh = false) => {
  const response = await axiosClient.post(
    `/api/controls/${controlId}/root-cause`,
    { session_id: sessionId, user_id: userId },
    { params: { refresh } }
  );
  return response.data;
};

const triggerEnrichment = async (controlId, sessionId, userId, refresh = false) => {
  const response = await axiosClient.post(
    `/api/controls/${controlId}/enrichment`,
    { session_id: sessionId, user_id: userId },
    { params: { refresh } }
  );
  return response.data;
};

const controlsAPI = {
  search: async (id, limit = 100) => {
    const response = await axiosClient.get('/api/controls', {
      params: { id, limit }
    });
    return response.data;
  },

  getDetails: async (controlId) => {
    const response = await axiosClient.get(`/api/controls/${controlId}/details`);
    return response.data;
  },

  list: async (offset = 0, limit = 100) => {
    const response = await axiosClient.get('/api/controls/list', {
      params: { offset, limit }
    });
    return response.data;
  },

  aiTriggers: {
    controls_taxonomy: triggerControlsTaxonomy,
    root_cause: triggerRootCause,
    enrichment: triggerEnrichment
  },

  meta: {
    primaryFunction: 'controls_taxonomy',
    titleField: 'control_title',
    typeField: 'key_control',
    themeField: 'risk_theme',
    subthemeField: 'risk_subtheme',
    functionLabels: {
      controls_taxonomy: 'Controls Taxonomy',
      root_cause: 'Root Cause',
      enrichment: 'Enrichment'
    }
  }
};

export default controlsAPI;
