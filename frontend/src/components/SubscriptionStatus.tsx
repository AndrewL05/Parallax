import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Crown, Clock, TrendingUp, CheckCircle, XCircle } from 'lucide-react';
import { premiumService, SubscriptionAnalytics } from '../services/premiumService';
import { stripeService } from '../services/stripeService';

const SubscriptionStatus: React.FC = () => {
  const { getToken, isSignedIn } = useAuth();
  const [analytics, setAnalytics] = useState<SubscriptionAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isSignedIn) {
      fetchSubscriptionStatus();
    }
  }, [isSignedIn]);

  const fetchSubscriptionStatus = async () => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const data = await premiumService.getSubscriptionStatus(token);
      setAnalytics(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const startTrial = async () => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      await premiumService.startTrial(token, 7);
      await fetchSubscriptionStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start trial');
    }
  };

  const handleUpgrade = async () => {
    try {
      const token = await getToken();
      const checkout = await stripeService.createCheckoutSession('premium_monthly', token || undefined);
      if (checkout.url) {
        window.location.href = checkout.url;
      }
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      alert('Failed to start checkout. Please try again.');
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'premium':
        return 'bg-gradient-to-r from-yellow-400 to-orange-500';
      case 'enterprise':
        return 'bg-gradient-to-r from-purple-500 to-indigo-600';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusColor = (status: string, isActive: boolean) => {
    if (!isActive) return 'text-gray-500';
    switch (status.toLowerCase()) {
      case 'active':
        return 'text-green-600';
      case 'trial':
        return 'text-blue-600';
      case 'cancelled':
        return 'text-orange-600';
      default:
        return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !analytics) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <div className="text-center text-red-600">
            <XCircle className="mx-auto h-12 w-12 mb-4" />
            <p>{error || 'Failed to load subscription data'}</p>
            <Button onClick={fetchSubscriptionStatus} className="mt-4">
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { subscription, usage, features } = analytics;

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Main Subscription Card */}
      <Card className="overflow-hidden">
        <CardHeader className={`text-white ${getTierColor(subscription.tier)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Crown className="h-8 w-8" />
              <div>
                <CardTitle className="text-2xl font-bold capitalize">
                  {subscription.tier} Plan
                </CardTitle>
                <p className="opacity-90">
                  {subscription.is_trial ? 'Trial Period' : 'Active Subscription'}
                </p>
              </div>
            </div>
            <Badge
              variant={subscription.is_active ? 'default' : 'secondary'}
              className={`${getStatusColor(subscription.status, subscription.is_active)} bg-white text-current`}
            >
              {subscription.status.toUpperCase()}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Usage Stats */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Usage This Month
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Simulations</span>
                  <span className="font-medium">
                    {usage.simulations_used}
                    {usage.simulations_limit && ` / ${usage.simulations_limit}`}
                  </span>
                </div>
                {usage.simulations_limit && (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{
                        width: `${Math.min((usage.simulations_used / usage.simulations_limit) * 100, 100)}%`
                      }}
                    ></div>
                  </div>
                )}
              </div>
            </div>

            {/* Billing Info */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg flex items-center">
                <Clock className="h-5 w-5 mr-2" />
                Billing
              </h3>
              <div className="space-y-2">
                {subscription.billing_period && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Period</span>
                    <span className="font-medium capitalize">{subscription.billing_period}</span>
                  </div>
                )}
                {subscription.days_until_expiry !== null && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Days Remaining</span>
                    <span className="font-medium">{subscription.days_until_expiry}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Quick Actions</h3>
              <div className="space-y-2">
                {subscription.tier === 'free' && (
                  <>
                    <Button onClick={startTrial} className="w-full" variant="outline">
                      Start 7-Day Trial
                    </Button>
                    <Button onClick={handleUpgrade} className="w-full" variant="primary">
                      Upgrade to Premium
                    </Button>
                  </>
                )}
                {subscription.tier === 'premium' && (
                  <Button variant="outline" className="w-full">
                    Manage Subscription
                  </Button>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <FeatureCard
          title="Advanced Simulations"
          enabled={features.advanced_simulations}
          description="Enhanced AI analysis with risk assessment and market conditions"
        />
        <FeatureCard
          title="AI Chatbot"
          enabled={features.ai_chatbot_access}
          description="Personalized insights and guidance based on your simulation history"
        />
        <FeatureCard
          title="Custom Scenarios"
          enabled={features.custom_scenarios}
          description="Create and share your own simulation scenarios"
        />
        <FeatureCard
          title="Export Formats"
          enabled={features.export_formats.length > 1}
          description={`Export in ${features.export_formats.join(', ')} formats`}
        />
        <FeatureCard
          title="Priority Support"
          enabled={features.priority_support}
          description="Fast response times and dedicated support team"
        />
        <FeatureCard
          title="Historical Data"
          enabled={features.historical_data_months > 1}
          description={`Access ${features.historical_data_months} months of historical data`}
        />
      </div>
    </div>
  );
};

interface FeatureCardProps {
  title: string;
  enabled: boolean;
  description: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ title, enabled, description }) => (
  <Card className={`transition-all duration-200 ${enabled ? 'border-green-200 bg-green-50' : 'border-gray-200'}`}>
    <CardContent className="p-4">
      <div className="flex items-start space-x-3">
        {enabled ? (
          <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
        ) : (
          <XCircle className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
        )}
        <div>
          <h4 className={`font-medium ${enabled ? 'text-green-900' : 'text-gray-700'}`}>
            {title}
          </h4>
          <p className={`text-sm mt-1 ${enabled ? 'text-green-700' : 'text-gray-500'}`}>
            {description}
          </p>
        </div>
      </div>
    </CardContent>
  </Card>
);

export default SubscriptionStatus;