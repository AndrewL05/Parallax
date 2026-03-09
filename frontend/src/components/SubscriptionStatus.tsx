import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@clerk/clerk-react';
import { Check, X } from 'lucide-react';
import { premiumService, SubscriptionAnalytics } from '../services/premiumService';
import { stripeService } from '../services/stripeService';

const SubscriptionStatus: React.FC = () => {
  const { getToken, isSignedIn } = useAuth();
  const [analytics, setAnalytics] = useState<SubscriptionAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isSignedIn) fetchSubscriptionStatus();
  }, [isSignedIn]);

  const fetchSubscriptionStatus = async () => {
    try {
      const token = await getToken();
      if (!token) throw new Error('Not authenticated');
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
      if (!token) throw new Error('Not authenticated');
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
      if (checkout.url) window.location.href = checkout.url;
    } catch {
      alert('Failed to start checkout. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto pt-12">
        <div className="animate-pulse space-y-6">
          <div className="h-5 bg-stone-200 rounded-lg w-32" />
          <div className="h-32 bg-stone-100 rounded-xl" />
          <div className="grid grid-cols-3 gap-4">
            {[1, 2, 3].map(i => <div key={i} className="h-20 bg-stone-100 rounded-xl" />)}
          </div>
        </div>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="max-w-3xl mx-auto pt-12 text-center">
        <p className="text-stone-500 text-sm mb-4">{error || 'Failed to load subscription data'}</p>
        <button onClick={fetchSubscriptionStatus}
          className="px-5 py-2.5 bg-stone-950 text-white text-sm font-medium rounded-xl hover:bg-stone-800 transition-colors">
          Try again
        </button>
      </div>
    );
  }

  const { subscription, usage, features } = analytics;
  const isPremium = subscription.tier === 'premium' && subscription.is_active;
  const usagePercent = usage.simulations_limit
    ? Math.min((usage.simulations_used / usage.simulations_limit) * 100, 100)
    : null;

  return (
    <motion.div className="max-w-3xl mx-auto" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
      <h2 className="text-3xl sm:text-4xl font-bold text-stone-900 mb-2">Account</h2>
      <p className="text-stone-400 text-sm mb-10">Manage your plan and usage</p>

      {/* Plan overview */}
      <div className={`rounded-xl p-6 sm:p-8 mb-6 ${isPremium ? 'bg-stone-950 text-white' : 'bg-white border-2 border-stone-200'}`}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className={`text-xs tracking-widest uppercase mb-1 ${isPremium ? 'text-stone-500' : 'text-stone-400'}`}>Current plan</p>
            <p className={`text-2xl font-bold capitalize ${isPremium ? 'text-white' : 'text-stone-900'}`}>
              {subscription.tier}
            </p>
          </div>
          <span className={`px-3 py-1 text-xs font-medium rounded-full ${
            subscription.is_active
              ? isPremium ? 'bg-white/10 text-white' : 'bg-stone-100 text-stone-600'
              : 'bg-stone-100 text-stone-400'
          }`}>
            {subscription.is_trial ? 'Trial' : subscription.status}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          {subscription.billing_period && (
            <div>
              <p className={`text-xs ${isPremium ? 'text-stone-500' : 'text-stone-400'}`}>Billing</p>
              <p className={`text-sm font-medium capitalize ${isPremium ? 'text-white' : 'text-stone-900'}`}>{subscription.billing_period}</p>
            </div>
          )}
          {subscription.days_until_expiry !== null && (
            <div>
              <p className={`text-xs ${isPremium ? 'text-stone-500' : 'text-stone-400'}`}>Days remaining</p>
              <p className={`text-sm font-medium ${isPremium ? 'text-white' : 'text-stone-900'}`}>{subscription.days_until_expiry}</p>
            </div>
          )}
          <div>
            <p className={`text-xs ${isPremium ? 'text-stone-500' : 'text-stone-400'}`}>Simulations</p>
            <p className={`text-sm font-medium ${isPremium ? 'text-white' : 'text-stone-900'}`}>
              {usage.simulations_used}{usage.simulations_limit ? ` / ${usage.simulations_limit}` : ' used'}
            </p>
          </div>
        </div>

        {usagePercent !== null && (
          <div className="mt-5">
            <div className={`w-full h-1.5 rounded-full ${isPremium ? 'bg-white/10' : 'bg-stone-100'}`}>
              <div className={`h-1.5 rounded-full transition-all duration-500 ${isPremium ? 'bg-white/60' : 'bg-stone-900'}`}
                style={{ width: `${usagePercent}%` }} />
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      {subscription.tier === 'free' && (
        <div className="flex gap-3 mb-10">
          <button onClick={startTrial}
            className="flex-1 py-3 border-2 border-stone-300 rounded-xl text-sm font-medium text-stone-700 hover:border-stone-500 transition-colors">
            Start 7-day trial
          </button>
          <button onClick={handleUpgrade}
            className="flex-1 py-3 bg-stone-950 text-white rounded-xl text-sm font-medium hover:bg-stone-800 transition-colors">
            Upgrade to Premium
          </button>
        </div>
      )}
      {subscription.tier === 'premium' && (
        <div className="mb-10">
          <button className="w-full py-3 border-2 border-stone-300 rounded-xl text-sm font-medium text-stone-700 hover:border-stone-500 transition-colors">
            Manage subscription
          </button>
        </div>
      )}

      {/* Features */}
      <p className="text-xs tracking-widest uppercase text-stone-400 mb-4">Features</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-px bg-stone-200 rounded-xl overflow-hidden mb-6">
        <FeatureRow label="Advanced simulations" enabled={features.advanced_simulations} />
        <FeatureRow label="AI chatbot" enabled={features.ai_chatbot_access} />
        <FeatureRow label="Custom scenarios" enabled={features.custom_scenarios} />
        <FeatureRow label="Priority support" enabled={features.priority_support} />
        <FeatureRow label="Export formats" enabled={features.export_formats.length > 1}
          detail={features.export_formats.join(', ').toUpperCase()} />
        <FeatureRow label="History" enabled={features.historical_data_months > 1}
          detail={`${features.historical_data_months} months`} />
      </div>
    </motion.div>
  );
};

const FeatureRow: React.FC<{ label: string; enabled: boolean; detail?: string }> = ({ label, enabled, detail }) => (
  <div className="bg-white p-4 flex items-center justify-between">
    <div className="flex items-center gap-3">
      <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${
        enabled ? 'bg-stone-900' : 'bg-stone-200'
      }`}>
        {enabled
          ? <Check size={12} className="text-white" strokeWidth={2.5} />
          : <X size={10} className="text-stone-400" strokeWidth={2.5} />
        }
      </div>
      <span className={`text-sm ${enabled ? 'text-stone-900' : 'text-stone-400'}`}>{label}</span>
    </div>
    {detail && <span className="text-xs text-stone-400">{detail}</span>}
  </div>
);

export default SubscriptionStatus;
