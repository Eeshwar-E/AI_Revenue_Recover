import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
});

const request = <T = any>(promise: Promise<{ data: T }>) =>
  promise.then((response) => response.data);

// Dashboard APIs
export const getSummary = () => request(api.get('/api/dashboard/summary'));
export const getRecovery = () => request(api.get('/api/dashboard/recovery'));
export const getRiskDistribution = () => request(api.get('/api/dashboard/risk-distribution'));
export const getFunnel = () => request(api.get('/api/dashboard/funnel'));
export const getFailureReasons = () => request(api.get('/api/dashboard/failure-reasons'));

// Cases APIs
export const casesAPI = {
  getAll: (params?: Record<string, string>) => request(api.get('/api/cases', { params })),
  getDetail: (id: string | number) => request(api.get(`/api/cases/${id}`)),
  runCase: (id: string | number) => request(api.post(`/api/cases/${id}/run`)),
  approve: (id: string | number) => request(api.post(`/api/cases/${id}/approve`)),
  stop: (id: string | number) => request(api.post(`/api/cases/${id}/stop`)),
  retry: (id: string | number) => request(api.post(`/api/cases/${id}/retry`)),
};

// Agent APIs
export const agentAPI = {
  analyze: (id: string | number) => request(api.post(`/api/agent/analyze/${id}`)),
  run: (id: string | number) => request(api.post(`/api/agent/run/${id}`)),
};

// Batch APIs
export const batchAPI = {
  analyze: () => request(api.post('/api/batch/analyze')),
  run: () => request(api.post('/api/batch/run')),
};

// Audit APIs
export const auditAPI = {
  getByCase: (caseId: string | number) => request(api.get(`/api/audit/${caseId}`)),
  getAll: (params?: Record<string, number>) => request(api.get('/api/audit', { params })),
};

// Simulation APIs
export const simulationAPI = {
  seed: () => api.post('/api/simulation/seed'),
  run: () => api.post('/api/simulation/run'),
  demoReset: () => api.post('/api/simulation/demo/reset'),
  demoRun: () => api.post('/api/simulation/demo/run'),
}