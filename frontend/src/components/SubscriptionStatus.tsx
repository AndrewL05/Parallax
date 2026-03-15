import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@clerk/clerk-react';
import { Check, X, Clock, TrendingUp, ArrowUpRight } from 'lucide-react';
import { premiumService, SubscriptionAnalytics } from '../services/premiumService';
import { simulationService } from '../services/simulationService';
import { stripeService } from '../services/stripeService';
import { ApiError } from '../services/api';
import type { SimulationResult } from '../types/api';

interface SubscriptionStatusProps {
  onViewSimulation?: (simulation: SimulationResult) => void;
}

const SubscriptionStatus: React.FC<SubscriptionStatusProps> = ({ onViewSimulation }) => {
  const { getToken, isSignedIn } = useAuth();
  const [analytics, setAnalytics] = useState<SubscriptionAnalytics | null>(null);
  const [history, setHistory] = useState<SimulationResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [popupMessage, setPopupMessage] = useState<string | null>(null);
  const [showManage, setShowManage] = useState(false);
  const [cancelConfirm, setCancelConfirm] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (isSignedIn) {
      fetchSubscriptionStatus();
      fetchHistory();
    }
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

  const fetchHistory = async () => {
    try {
      const token = await getToken();
      if (!token) return;
      const sims = await simulationService.getUserSimulations(token);
      setHistory(sims);
    } catch {
      // history fetch failure is not critical
    } finally {
      setHistoryLoading(false);
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
    } catch (error) {
      if (error instanceof ApiError && error.status === 400 && error.message.toLowerCase().includes('already have')) {
        setPopupMessage('already_premium');
      } else {
        setPopupMessage(error instanceof Error ? error.message : 'Failed to start checkout.');
      }
    }
  };

  const handleCancel = async () => {
    try {
      setCancelling(true);
      const token = await getToken();
      if (!token) throw new Error('Not authenticated');
      await premiumService.cancelSubscription(token);
      setCancelConfirm(false);
      setShowManage(false);
      await fetchSubscriptionStatus();
    } catch (err) {
      setPopupMessage(err instanceof Error ? err.message : 'Failed to cancel subscription.');
    } finally {
      setCancelling(false);
    }
  };

  const renderPlanSection = () => {
    if (!analytics) return null;
    const { subscription, usage, features } = analytics;
    const isPremium = subscription.tier === 'premium' && subscription.is_active;
    const usagePercent = usage.simulations_limit
      ? Math.min((usage.simulations_used / usage.simulations_limit) * 100, 100)
      : null;

    return (
      <>
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
            <button
              onClick={() => { setShowManage(true); setCancelConfirm(false); }}
              className="w-full py-3 border-2 border-stone-300 rounded-xl text-sm font-medium text-stone-700
                hover:border-stone-500 hover:bg-stone-50 active:scale-[0.995] transition-colors"
            >
              Manage subscription
            </button>
          </div>
        )}

        {/* Features */}
        <p className="text-xs tracking-widest uppercase text-stone-400 mb-4">Features</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-px bg-stone-200 rounded-xl overflow-hidden mb-10">
          <FeatureRow label="Advanced simulations" enabled={features.advanced_simulations} />
          <FeatureRow label="AI chatbot" enabled={features.ai_chatbot_access} />
          <FeatureRow label="Custom scenarios" enabled={features.custom_scenarios} />
          <FeatureRow label="Priority support" enabled={features.priority_support} />
          <FeatureRow label="Export formats" enabled={features.export_formats.length > 1}
            detail={features.export_formats.join(', ').toUpperCase()} />
          <FeatureRow label="History" enabled={features.historical_data_months > 1}
            detail={`${features.historical_data_months} months`} />
        </div>
      </>
    );
  };

  return (
    <motion.div className="max-w-3xl mx-auto" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
      <h2 className="text-3xl sm:text-4xl font-bold text-stone-900 mb-2">Account</h2>
      <p className="text-stone-400 text-sm mb-10">Manage your plan and usage</p>

      {/* Plan overview */}
      {loading ? (
        <div className="animate-pulse space-y-6 mb-10">
          <div className="h-32 bg-stone-100 rounded-xl" />
          <div className="grid grid-cols-3 gap-4">
            {[1, 2, 3].map(i => <div key={i} className="h-20 bg-stone-100 rounded-xl" />)}
          </div>
        </div>
      ) : error || !analytics ? (
        <div className="bg-white border-2 border-stone-200 rounded-xl p-6 sm:p-8 mb-10">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-xs tracking-widest uppercase mb-1 text-stone-400">Current plan</p>
              <p className="text-2xl font-bold text-stone-900">Free</p>
            </div>
            <span className="px-3 py-1 text-xs font-medium rounded-full bg-stone-100 text-stone-400">
              offline
            </span>
          </div>
          <p className="text-stone-400 text-xs mb-4">Could not load subscription details. </p>
          <button onClick={fetchSubscriptionStatus}
            className="px-4 py-2 border-2 border-stone-300 rounded-xl text-xs font-medium text-stone-700 hover:border-stone-500 transition-colors">
            Retry
          </button>
        </div>
      ) : (
        renderPlanSection()
      )}

      {/* Simulation History */}
      <p className="text-xs tracking-widest uppercase text-stone-400 mb-4">Simulation history</p>

      {historyLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse h-[88px] bg-stone-100 rounded-xl" />
          ))}
        </div>
      ) : history.length === 0 ? (
        <div className="bg-white border-2 border-dashed border-stone-200 rounded-xl p-8 text-center">
          <div className="w-10 h-10 rounded-full bg-stone-100 flex items-center justify-center mx-auto mb-3">
            <Clock size={18} className="text-stone-400" />
          </div>
          <p className="text-sm font-medium text-stone-900 mb-1">No simulations yet</p>
          <p className="text-xs text-stone-400">Your simulation history will appear here</p>
        </div>
      ) : (
        <div className="space-y-2">
          {history.map((sim, idx) => (
            <HistoryCard
              key={sim.id}
              simulation={sim}
              index={idx}
              onView={() => onViewSimulation?.(sim)}
            />
          ))}
        </div>
      )}

      {/* Manage subscription drawer */}
      {showManage && analytics && (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 backdrop-blur-sm
            animate-[fadeIn_0.1s_ease-out]"
          onClick={() => { setShowManage(false); setCancelConfirm(false); }}
        >
          <div
            className="bg-white w-full max-w-lg rounded-t-2xl shadow-float
              animate-[slideUp_0.25s_cubic-bezier(0.16,1,0.3,1)]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Drag handle */}
            <div className="flex justify-center pt-3 pb-1">
              <div className="w-10 h-1 rounded-full bg-stone-200" />
            </div>

            <div className="px-6 sm:px-8 pt-4 pb-8">
              <h3 className="text-lg font-semibold text-stone-900 font-display mb-1">
                Manage subscription
              </h3>
              <p className="text-sm text-stone-400 mb-6">Premium plan details and options</p>

              {/* Plan details grid */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-stone-50 rounded-xl p-4">
                  <p className="text-[11px] tracking-widest uppercase text-stone-400 mb-1">Plan</p>
                  <p className="text-sm font-medium text-stone-900">
                    Premium
                  </p>
                </div>
                <div className="bg-stone-50 rounded-xl p-4">
                  <p className="text-[11px] tracking-widest uppercase text-stone-400 mb-1">Billing</p>
                  <p className="text-sm font-medium text-stone-900 capitalize">
                    {analytics.subscription.billing_period || 'Monthly'}
                  </p>
                </div>
                <div className="bg-stone-50 rounded-xl p-4">
                  <p className="text-[11px] tracking-widest uppercase text-stone-400 mb-1">Status</p>
                  <p className="text-sm font-medium text-stone-900">
                    {analytics.subscription.is_trial ? 'Trial' : 'Active'}
                  </p>
                </div>
                <div className="bg-stone-50 rounded-xl p-4">
                  <p className="text-[11px] tracking-widest uppercase text-stone-400 mb-1">
                    {analytics.subscription.is_trial ? 'Trial ends in' : 'Renews in'}
                  </p>
                  <p className="text-sm font-medium text-stone-900">
                    {analytics.subscription.days_until_expiry != null
                      ? `${analytics.subscription.days_until_expiry} days`
                      : '—'}
                  </p>
                </div>
              </div>

              {/* Divider */}
              <div className="h-px bg-stone-100 mb-6" />

              {/* Cancel section */}
              {!cancelConfirm ? (
                <div className="flex gap-3">
                  <button
                    onClick={() => { setShowManage(false); setCancelConfirm(false); }}
                    className="flex-1 py-3 bg-stone-900 text-white rounded-xl text-sm font-medium
                      hover:bg-stone-800 active:scale-[0.98] transition-colors"
                  >
                    Done
                  </button>
                  <button
                    onClick={() => setCancelConfirm(true)}
                    className="py-3 px-5 rounded-xl text-sm font-medium text-stone-400
                      hover:text-red-500 hover:bg-red-50 active:scale-[0.98] transition-colors"
                  >
                    Cancel plan
                  </button>
                </div>
              ) : (
                <div className="animate-[popIn_0.15s_ease-out]">
                  <div className="bg-red-50 border border-red-100 rounded-xl p-4 mb-4">
                    <p className="text-sm text-red-800 font-medium mb-1">Cancel your subscription?</p>
                    <p className="text-sm text-red-600/70">
                      You'll keep access until the end of your current billing period, then revert to the free plan.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => setCancelConfirm(false)}
                      className="flex-1 py-3 bg-stone-900 text-white rounded-xl text-sm font-medium
                        hover:bg-stone-800 active:scale-[0.98] transition-colors"
                    >
                      Keep premium
                    </button>
                    <button
                      onClick={handleCancel}
                      disabled={cancelling}
                      className="flex-1 py-3 border-2 border-red-200 text-red-600 rounded-xl text-sm font-medium
                        hover:bg-red-50 hover:border-red-300 disabled:opacity-50 active:scale-[0.98] transition-colors"
                    >
                      {cancelling ? 'Cancelling...' : 'Yes, cancel'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Popup notification */}
      {popupMessage && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
          onClick={() => setPopupMessage(null)}
        >
          <div
            className="bg-white rounded-2xl shadow-elevated py-10 px-10 w-full max-w-md mx-4 text-center animate-[popIn_0.15s_ease-out]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="w-12 h-12 bg-accent-50 rounded-full flex items-center justify-center mx-auto mb-5">
              <svg className="w-6 h-6 text-accent-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20 10 10 0 000-20z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-stone-900 mb-2 font-display">
              {popupMessage === 'already_premium' ? 'Already Premium' : 'Checkout Error'}
            </h3>
            <p className="text-sm text-stone-500 mb-8">
              {popupMessage === 'already_premium'
                ? 'You already have a premium subscription.'
                : popupMessage}
            </p>
            <button
              onClick={() => setPopupMessage(null)}
              className="w-full py-3.5 bg-stone-900 text-white rounded-xl text-sm font-semibold hover:bg-stone-800 transition-colors"
            >
              Got it
            </button>
          </div>
        </div>
      )}
    </motion.div>
  );
};

const HistoryCard: React.FC<{
  simulation: SimulationResult;
  index: number;
  onView: () => void;
}> = ({ simulation, index, onView }) => {
  const pathA = simulation.choice_a_timeline;
  const pathB = simulation.choice_b_timeline;
  const titleA = pathA[0]?.career_title || 'Path A';
  const titleB = pathB[0]?.career_title || 'Path B';
  const lastA = pathA[pathA.length - 1];
  const lastB = pathB[pathB.length - 1];
  const salaryA = lastA?.salary;
  const salaryB = lastB?.salary;

  const date = new Date(simulation.created_at);
  const relative = getRelativeTime(date);

  return (
    <motion.button
      onClick={onView}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.25 }}
      className="w-full text-left bg-white border-2 border-stone-200 rounded-xl p-4 sm:p-5 group
        hover:border-stone-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-stone-300
        active:scale-[0.99] transition-colors"
    >
      <div className="flex items-center justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-medium text-stone-900 truncate">{titleA}</span>
            <span className="text-stone-300 text-xs flex-shrink-0">vs</span>
            <span className="text-sm font-medium text-stone-900 truncate">{titleB}</span>
          </div>
          <div className="flex items-center gap-4 text-xs text-stone-400">
            <span className="flex items-center gap-1">
              <Clock size={11} />
              {relative}
            </span>
            {salaryA != null && (
              <span className="flex items-center gap-1">
                <TrendingUp size={11} />
                ${Math.round(salaryA / 1000)}k
                <span className="text-stone-300">/</span>
                ${Math.round((salaryB ?? 0) / 1000)}k
              </span>
            )}
          </div>
        </div>
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-stone-100 flex items-center justify-center
          group-hover:bg-stone-900 transition-colors">
          <ArrowUpRight size={13} className="text-stone-400 group-hover:text-white transition-colors" />
        </div>
      </div>
    </motion.button>
  );
};

function getRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  if (diffDay < 7) return `${diffDay}d ago`;
  if (diffDay < 30) return `${Math.floor(diffDay / 7)}w ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

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
