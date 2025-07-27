import { apiService } from './api';

class StripeService {
  async createCheckoutSession(packageType, token) {
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    return apiService.post(`/payments/checkout?package=${packageType}`, {}, headers);
  }

  async getPaymentStatus(sessionId) {
    return apiService.get(`/payments/status/${sessionId}`);
  }

  async pollPaymentStatus(sessionId, maxAttempts = 5) {
    const pollInterval = 2000; // 2 seconds
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const status = await this.getPaymentStatus(sessionId);
        
        if (status.payment_status === 'paid') {
          return { success: true, status };
        } else if (status.payment_status === 'expired') {
          return { success: false, status, reason: 'expired' };
        }
        
        // Wait before next attempt
        if (attempt < maxAttempts - 1) {
          await new Promise(resolve => setTimeout(resolve, pollInterval));
        }
      } catch (error) {
        console.error('Error polling payment status:', error);
        if (attempt === maxAttempts - 1) {
          return { success: false, error: error.message };
        }
      }
    }
    
    return { success: false, reason: 'timeout' };
  }
}

export const stripeService = new StripeService();