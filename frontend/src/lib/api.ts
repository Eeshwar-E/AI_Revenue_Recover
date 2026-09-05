import axios from 'axios';

const api = axios.create({
  // Local dev: Vite proxies /api/* -> http://localhost:8000 (see vite.config.ts).
  baseURL: '/api',
  timeout: 10000,
});

// Long timeout for full-batch recovery (72 cases can exceed 10s).
const batchApi = axios.create({ baseURL: '/api', timeout: 120000 });
const batchRequest = <T = any>(promise: Promise<{ data: T }>) =>
  promise.then((response) => response.data);

const request = <T = any>(promise: Promise<{ data: T }>) =>
  promise.then((response) => response.data);

// Dashboard APIs
export const getSummary = () => request(api.get('/dashboard/summary'));
export const getRecovery = () => request(api.get('/dashboard/recovery'));
export const getRiskDistribution = () => request(api.get('/dashboard/risk-distribution'));
export const getFunnel = () => request(api.get('/dashboard/funnel'));
export const getFailureReasons = () => request(api.get('/dashboard/failure-reasons'));

// Cases APIs
export const casesAPI = {
  getAll: (params?: Record<string, string>) => request(api.get('/cases', { params })),
  getDetail: (id: string | number) => request(api.get(`/cases/${id}`)),
  runCase: (id: string | number) => request(api.post(`/cases/${id}/run`)),
  approve: (id: string | number) => request(api.post(`/cases/${id}/approve`)),
  reject: (id: string | number) => request(api.post(`/cases/${id}/reject`)),
  escalate: (id: string | number) => request(api.post(`/cases/${id}/escalate`)),
  stop: (id: string | number) => request(api.post(`/cases/${id}/stop`)),
  retry: (id: string | number) => request(api.post(`/cases/${id}/retry`)),
};

// Agent APIs
export const agentAPI = {
  analyze: (id: string | number) => request(api.post(`/agent/analyze/${id}`)),
  run: (id: string | number) => request(api.post(`/agent/run/${id}`)),
  runs: () => request(api.get('/agent/runs')),
  decisions: (id: string | number) => request(api.get(`/agent/decisions/${id}`)),
};

// Batch APIs
export const batchAPI = {
  analyze: () => batchRequest(batchApi.post('/batch/analyze')),
  run: () => batchRequest(batchApi.post('/batch/run')),
};

// Audit APIs
export const auditAPI = {
  getByCase: (caseId: string | number) => request(api.get(`/audit/${caseId}`)),
  getAll: (params?: Record<string, number>) => request(api.get('/audit', { params })),
};

// Simulation APIs
export const simulationAPI = {
  seed: () => api.post('/simulation/seed'),
  run: () => api.post('/simulation/run'),
  demoReset: () => api.post('/simulation/demo/reset'),
  demoRun: () => api.post('/simulation/demo/run'),
}