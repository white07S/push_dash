// API service for external loss dataset
import axiosClient from './axiosClient';

const triggerIssueTaxonomy = async (referenceIdCode, refresh = false) => {
  const response = await axiosClient.post(
    `/api/external-loss/${referenceIdCode}/issue-taxonomy`,
    null,
    { params: { refresh } }
  );
  return response.data;
};

const triggerRootCause = async (referenceIdCode, refresh = false) => {
  const response = await axiosClient.post(
    `/api/external-loss/${referenceIdCode}/root-cause`,
    null,
    { params: { refresh } }
  );
  return response.data;
};

const triggerEnrichment = async (referenceIdCode, refresh = false) => {
  const response = await axiosClient.post(
    `/api/external-loss/${referenceIdCode}/enrichment`,
    null,
    { params: { refresh } }
  );
  return response.data;
};

const externalLossAPI = {
  search: async (id, limit = 100) => {
    const response = await axiosClient.get('/api/external-loss', {
      params: { id, limit }
    });
    return response.data;
  },

  getDetails: async (referenceIdCode) => {
    const response = await axiosClient.get(`/api/external-loss/${referenceIdCode}/details`);
    return response.data;
  },

  list: async (offset = 0, limit = 100) => {
    const response = await axiosClient.get('/api/external-loss/list', {
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
    titleField: 'description_of_event',
    typeField: 'parent_name',
    themeField: 'risk_theme',
    subthemeField: 'risk_subtheme',
    functionLabels: {
      issue_taxonomy: 'Loss Taxonomy',
      root_cause: 'Root Cause',
      enrichment: 'Enrichment'
    }
  }
};

export default externalLossAPI;
