// Axios client configuration with interceptors
import axios from 'axios';

// Determine base URL based on current location
const getBaseURL = () => {
  const { hostname, protocol } = window.location;

  // If frontend is running on port 3000, backend is on port 8000
  if (window.location.port === '3000' || window.location.port === '3001') {
    return `${protocol}//${hostname}:8000`;
  }

  // Default to same host with port 8000
  return `${protocol}//${hostname}:8000`;
};

const axiosClient = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for logging
axiosClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and retry logic
axiosClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.method.toUpperCase(), response.config.url, response.status);
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 429 (Too Many Requests) and 503 (Service Unavailable) with retry
    if (
      (error.response?.status === 429 || error.response?.status === 503) &&
      !originalRequest._retry &&
      (!originalRequest._retryCount || originalRequest._retryCount < 2)
    ) {
      originalRequest._retry = true;
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;

      // Add jitter to retry delay (1-3 seconds)
      const delay = 1000 + Math.random() * 2000;
      console.log(`Retrying request after ${Math.round(delay)}ms...`);

      await new Promise(resolve => setTimeout(resolve, delay));
      return axiosClient(originalRequest);
    }

    // Log error details
    if (error.response) {
      console.error('API Error Response:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('API No Response:', error.message);
    } else {
      console.error('API Request Setup Error:', error.message);
    }

    return Promise.reject(error);
  }
);

export default axiosClient;
