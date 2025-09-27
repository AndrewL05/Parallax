import { apiService } from './api';
import type { SimulationData, SimulationResult, UserData } from '../types/api';

class SimulationService {
  async createSimulation(simulationData: SimulationData, token?: string): Promise<SimulationResult> {
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    return apiService.post<SimulationResult>('/simulate', simulationData, headers);
  }

  async getUserSimulations(token?: string): Promise<SimulationResult[]> {
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    return apiService.get<SimulationResult[]>('/simulations', headers);
  }

  async syncUserProfile(userData: UserData, token?: string): Promise<any> {
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    return apiService.post('/auth/sync', userData, headers);
  }
}

export const simulationService = new SimulationService();