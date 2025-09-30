import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useAuth } from "@clerk/clerk-react";
import { Download, TrendingUp, AlertTriangle, Lock } from "lucide-react";
import TimelineChart from "./TimelineChart";
import {
  premiumService,
  SubscriptionAnalytics,
} from "../services/premiumService";
import { stripeService } from "../services/stripeService";
import type { SimulationResult } from "../types/api";

interface SimulationResultsProps {
  simulation: SimulationResult;
  onNewSimulation: () => void;
}

const SimulationResults: React.FC<SimulationResultsProps> = ({
  simulation,
  onNewSimulation,
}) => {
  const { getToken, isSignedIn } = useAuth();
  const [subscription, setSubscription] =
    useState<SubscriptionAnalytics | null>(null);
  const [loadingSubscription, setLoadingSubscription] = useState(true);

  useEffect(() => {
    if (isSignedIn) {
      fetchSubscription();
    }
  }, [isSignedIn]);

  const fetchSubscription = async () => {
    try {
      const token = await getToken();
      if (token) {
        const data = await premiumService.getSubscriptionStatus(token);
        setSubscription(data);
      }
    } catch (error) {
      console.error("Failed to fetch subscription:", error);
    } finally {
      setLoadingSubscription(false);
    }
  };

  const isPremium =
    subscription?.subscription.tier === "premium" &&
    subscription?.subscription.is_active;

  const handleExport = async (format: "json" | "pdf" | "csv" | "excel") => {
    if (!isPremium && format !== "json") {
      alert("Premium subscription required for this export format");
      return;
    }

    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");

      const blob = await premiumService.exportSimulation(token, {
        simulation_id: simulation.id,
        format,
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `simulation-${simulation.id}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Export failed:", error);
      alert("Export failed. Please try again.");
    }
  };

  const handleUpgrade = async () => {
    try {
      const token = await getToken();
      const checkout = await stripeService.createCheckoutSession(
        "premium_monthly",
        token || undefined
      );
      if (checkout.url) {
        window.location.href = checkout.url;
      }
    } catch (error) {
      console.error("Failed to create checkout session:", error);
      alert("Failed to start checkout. Please try again.");
    }
  };

  const getLastTimelinePoint = (
    timeline: typeof simulation.choice_a_timeline
  ) => {
    return timeline[timeline.length - 1];
  };

  const calculateAverageHappiness = (
    timeline: typeof simulation.choice_a_timeline
  ): number => {
    const sum = timeline.reduce((acc, point) => acc + point.happiness_score, 0);
    return sum / timeline.length;
  };

  return (
    <motion.div
      className="max-w-7xl mx-auto"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-4xl font-bold text-gray-800 mb-2">
              Your Life Simulation Results
            </h2>
            <p className="text-gray-600 text-lg">
              Compare how your two life paths might unfold over the next 10
              years
            </p>
          </div>

          {/* Export Options */}
          <div className="flex gap-2">
            <button
              onClick={() => handleExport("json")}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              title="Export as JSON"
            >
              <Download size={16} />
              JSON
            </button>

            {isPremium ? (
              <>
                <button
                  onClick={() => handleExport("pdf")}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  title="Export as PDF"
                >
                  <Download size={16} />
                  PDF
                </button>
                <button
                  onClick={() => handleExport("csv")}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  title="Export as CSV"
                >
                  <Download size={16} />
                  CSV
                </button>
                <button
                  onClick={() => handleExport("excel")}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  title="Export as Excel"
                >
                  <Download size={16} />
                  Excel
                </button>
              </>
            ) : (
              <button
                onClick={handleUpgrade}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors"
                title="Upgrade for more export formats"
              >
                <Lock size={16} />
                Unlock Premium Exports
              </button>
            )}
          </div>
        </div>

        {/* Subscription Status Banner */}
        {!loadingSubscription && !isPremium && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-purple-100 to-pink-100 border border-purple-300 rounded-lg p-4 mb-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <AlertTriangle className="text-purple-600" size={24} />
                <div>
                  <h3 className="font-semibold text-purple-900">
                    Upgrade to Premium
                  </h3>
                  <p className="text-sm text-purple-700">
                    Get risk assessment, market analysis, unlimited simulations,
                    and more export formats
                  </p>
                </div>
              </div>
              <button
                onClick={handleUpgrade}
                className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors font-semibold"
              >
                Upgrade Now
              </button>
            </div>
          </motion.div>
        )}
      </div>

      {/* Timeline Visualizations */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
        <motion.div
          className="bg-white rounded-2xl shadow-xl p-6"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <TimelineChart
            data={simulation.choice_a_timeline}
            title="Path A Timeline"
            color="#2563EB"
          />
        </motion.div>

        <motion.div
          className="bg-white rounded-2xl shadow-xl p-6"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <TimelineChart
            data={simulation.choice_b_timeline}
            title="Path B Timeline"
            color="#059669"
          />
        </motion.div>
      </div>

      {/* Summary */}
      <motion.div
        className="bg-white rounded-2xl shadow-xl p-8 mb-8"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <h3 className="text-2xl font-bold text-gray-800 mb-4">
          AI Analysis & Insights
        </h3>
        <p className="text-gray-700 leading-relaxed text-lg">
          {simulation.summary}
        </p>
      </motion.div>

      {/* Premium Features Section */}
      {isPremium && (
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          {/* Risk Assessment */}
          <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl p-6 border-2 border-orange-200">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="text-orange-600" size={24} />
              <h3 className="text-xl font-bold text-orange-900">
                Risk Assessment
              </h3>
              <span className="ml-auto px-3 py-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-semibold rounded-full">
                PREMIUM
              </span>
            </div>
            <div className="space-y-3">
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 mb-2">
                  Path A Risks
                </h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Market volatility impact on career trajectory</li>
                  <li>• Work-life balance considerations</li>
                  <li>• Financial stability factors</li>
                </ul>
              </div>
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 mb-2">
                  Path B Risks
                </h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Industry disruption potential</li>
                  <li>• Skill obsolescence considerations</li>
                  <li>• Income stability factors</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Market Conditions Analysis */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border-2 border-blue-200">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="text-blue-600" size={24} />
              <h3 className="text-xl font-bold text-blue-900">
                Market Analysis
              </h3>
              <span className="ml-auto px-3 py-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-semibold rounded-full">
                PREMIUM
              </span>
            </div>
            <div className="space-y-3">
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 mb-2">
                  Industry Trends
                </h4>
                <p className="text-sm text-gray-600">
                  Current market conditions favor adaptable professionals with
                  diverse skill sets. Technology integration continues to
                  reshape traditional career paths.
                </p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 mb-2">
                  Economic Outlook
                </h4>
                <p className="text-sm text-gray-600">
                  Projected growth in key sectors suggests stable opportunities,
                  with emphasis on continuous learning and skill development.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Locked Premium Features (for free users) */}
      {!isPremium && !loadingSubscription && (
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <div className="relative bg-gray-100 rounded-2xl p-6 border-2 border-gray-300 opacity-60">
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 rounded-2xl">
              <div className="text-center">
                <Lock className="mx-auto mb-2 text-white" size={40} />
                <p className="text-white font-semibold">Risk Assessment</p>
                <p className="text-gray-200 text-sm">Upgrade to Premium</p>
              </div>
            </div>
            <div className="blur-sm">
              <h3 className="text-xl font-bold mb-4">Risk Assessment</h3>
              <div className="space-y-3">
                <div className="bg-white rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Path A Risks</h4>
                  <p className="text-sm">Detailed risk analysis...</p>
                </div>
              </div>
            </div>
          </div>

          <div className="relative bg-gray-100 rounded-2xl p-6 border-2 border-gray-300 opacity-60">
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 rounded-2xl">
              <div className="text-center">
                <Lock className="mx-auto mb-2 text-white" size={40} />
                <p className="text-white font-semibold">Market Analysis</p>
                <p className="text-gray-200 text-sm">Upgrade to Premium</p>
              </div>
            </div>
            <div className="blur-sm">
              <h3 className="text-xl font-bold mb-4">Market Analysis</h3>
              <div className="space-y-3">
                <div className="bg-white rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Industry Trends</h4>
                  <p className="text-sm">Market analysis...</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Quick Stats Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Path A Stats */}
        <motion.div
          className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <h4 className="text-xl font-bold text-blue-800 mb-4">
            Path A Highlights
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-blue-700">10-Year Salary:</span>
              <span className="font-semibold">
                $
                {getLastTimelinePoint(
                  simulation.choice_a_timeline
                )?.salary?.toLocaleString() || "N/A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Avg Happiness:</span>
              <span className="font-semibold">
                {calculateAverageHappiness(
                  simulation.choice_a_timeline
                ).toFixed(1)}
                /10
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Final Role:</span>
              <span className="font-semibold">
                {getLastTimelinePoint(simulation.choice_a_timeline)
                  ?.career_title || "N/A"}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Path B Stats */}
        <motion.div
          className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 1.0 }}
        >
          <h4 className="text-xl font-bold text-green-800 mb-4">
            Path B Highlights
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-green-700">10-Year Salary:</span>
              <span className="font-semibold">
                $
                {getLastTimelinePoint(
                  simulation.choice_b_timeline
                )?.salary?.toLocaleString() || "N/A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Avg Happiness:</span>
              <span className="font-semibold">
                {calculateAverageHappiness(
                  simulation.choice_b_timeline
                ).toFixed(1)}
                /10
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Final Role:</span>
              <span className="font-semibold">
                {getLastTimelinePoint(simulation.choice_b_timeline)
                  ?.career_title || "N/A"}
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="text-center">
        <motion.button
          onClick={onNewSimulation}
          className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-3 px-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Create New Simulation
        </motion.button>
      </div>
    </motion.div>
  );
};

export default SimulationResults;
