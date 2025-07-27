import { apiService } from './api';

class SimulationService {
  async createSimulation(simulationData, token) {
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    return apiService.post('/simulate', simulationData, headers);
  }

  async getUserSimulations(token) {
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    return apiService.get('/simulations', headers);
  }

  async syncUserProfile(userData, token) {
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    return apiService.post('/auth/sync', userData, headers);
  }
}

export const simulationService = new SimulationService();