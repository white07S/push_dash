// API service for issues dataset
import axiosClient from './axiosClient';

const triggerIssueTaxonomy = async (issueId, description = null, refresh = false) => {
  const response = await axiosClient.post(
    `/api/issues/${issueId}/issue-taxonomy`,
    { description },
    { params: { refresh } }
  );
  return response.data;
};

const triggerRootCause = async (issueId, description = null, refresh = false) => {
  const response = await axiosClient.post(
    `/api/issues/${issueId}/root-cause`,
    { description },
    { params: { refresh } }
  );
  return response.data;
};

const triggerEnrichment = async (issueId, description = null, refresh = false) => {
  const response = await axiosClient.post(
    `/api/issues/${issueId}/enrichment`,
    { description },
    { params: { refresh } }
  );
  return response.data;
};

const issuesAPI = {
  search: async (id, limit = 100) => {
    const response = await axiosClient.get('/api/issues', {
      params: { id, limit }
    });
    return response.data;
  },

  getDetails: async (issueId) => {
    const response = await axiosClient.get(`/api/issues/${issueId}/details`);
    return response.data;
  },

  list: async (offset = 0, limit = 100) => {
    const response = await axiosClient.get('/api/issues/list', {
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
    titleField: 'issue_title',
    typeField: 'issues_type',
    themeField: 'risk_theme',
    subthemeField: 'risk_subtheme',
    functionLabels: {
      issue_taxonomy: 'Issue Taxonomy',
      root_cause: 'Root Cause',
      enrichment: 'Enrichment'
    }
  }
};

export default issuesAPI;
