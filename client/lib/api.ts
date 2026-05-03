import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const seedDatabase = () => api.post('/demo/seed');
export const getFullAnalysis = () => api.get('/demo/full-analysis');
export const getFraudNetwork = () => api.get('/demo/fraud-network');
export const getCollusionRisk = (bidderId: string) => api.get(`/demo/collusion-risk/${bidderId}`);