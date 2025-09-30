import { apiService } from './api';

interface PaymentStatus {
  payment_status: 'paid' | 'pending' | 'expired' | 'canceled';
  session_id: string;
  created_at?: string;
}

interface PaymentPollResult {
  success: boolean;
  status?: PaymentStatus;
  reason?: 'expired' | 'timeout';
  error?: string;
}

class StripeService {
  async createCheckoutSession(packageType: string, token?: string): Promise<{ url: string; session_id: string }> {
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    const response = await apiService.post<{ checkout_url: string; session_id: string }>(`/payments/checkout?package=${packageType}`, {}, headers);
    // Transform response to match expected format
    return {
      url: response.checkout_url,
      session_id: response.session_id
    };
  }

  async getPaymentStatus(sessionId: string): Promise<PaymentStatus> {
    return apiService.get<PaymentStatus>(`/payments/status/${sessionId}`);
  }

  async pollPaymentStatus(sessionId: string, maxAttempts: number = 5): Promise<PaymentPollResult> {
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
          return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
        }
      }
    }

    return { success: false, reason: 'timeout' };
  }
}

export const stripeService = new StripeService();