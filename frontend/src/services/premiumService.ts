import { apiService } from './api';

export interface SubscriptionInfo {
  tier: 'free' | 'premium' | 'enterprise';
  status: 'active' | 'inactive' | 'cancelled' | 'expired' | 'trial';
  is_active: boolean;
  is_trial: boolean;
  days_until_expiry: number | null;
  billing_period: string | null;
}

export interface UsageInfo {
  simulations_used: number;
  simulations_limit: number | null;
  features_used: Record<string, number>;
  period_start: string;
  period_end: string;
}

export interface FeatureAccess {
  advanced_simulations: boolean;
  ai_chatbot_access: boolean;
  export_formats: string[];
  priority_support: boolean;
  custom_scenarios: boolean;
  historical_data_months: number;
}

export interface SubscriptionAnalytics {
  subscription: SubscriptionInfo;
  usage: UsageInfo;
  features: FeatureAccess;
}

export interface AdvancedSimulationData {
  choice_a: string;
  choice_b: string;
  current_situation: string;
  goals: string;
  concerns: string;
  include_risk_assessment?: boolean;
  include_market_analysis?: boolean;
}

export interface ExportOptions {
  simulation_id: string;
  format: 'json' | 'pdf' | 'csv' | 'excel';
}

class PremiumService {
  async getSubscriptionStatus(token: string): Promise<SubscriptionAnalytics> {
    return apiService.get<SubscriptionAnalytics>(
      '/premium/subscription/status',
      { Authorization: `Bearer ${token}` }
    );
  }

  async startTrial(token: string, trialDays: number = 7): Promise<{ success: boolean; message: string }> {
    return apiService.post<{ success: boolean; message: string }>(
      '/payments/subscription/trial',
      { trial_days: trialDays },
      { Authorization: `Bearer ${token}` }
    );
  }

  async cancelSubscription(token: string): Promise<{ success: boolean; message: string }> {
    return apiService.post<{ success: boolean; message: string }>(
      '/payments/subscription/cancel',
      {},
      { Authorization: `Bearer ${token}` }
    );
  }

  async createAdvancedSimulation(token: string, data: AdvancedSimulationData): Promise<any> {
    return apiService.post<any>(
      '/premium/simulations/advanced',
      data,
      { Authorization: `Bearer ${token}` }
    );
  }

  async createCustomScenario(token: string, scenarioData: any): Promise<any> {
    return apiService.post<any>(
      '/premium/scenarios/custom',
      scenarioData,
      { Authorization: `Bearer ${token}` }
    );
  }

  async exportSimulation(token: string, options: ExportOptions): Promise<Blob> {
    const response = await fetch(
      `${import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'}/api/premium/simulations/export?simulation_id=${options.simulation_id}&format=${options.format}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error('Export failed');
    }

    return response.blob();
  }

  async getPremiumAnalytics(token: string): Promise<any> {
    return apiService.get<any>(
      '/premium/analytics/dashboard',
      { Authorization: `Bearer ${token}` }
    );
  }

  async getPrioritySupport(token: string): Promise<any> {
    return apiService.get<any>(
      '/premium/support/priority',
      { Authorization: `Bearer ${token}` }
    );
  }

  async submitPremiumFeedback(token: string, feedback: { subject: string; message: string }): Promise<any> {
    return apiService.post<any>(
      '/premium/feedback/premium',
      feedback,
      { Authorization: `Bearer ${token}` }
    );
  }
}

export const premiumService = new PremiumService();