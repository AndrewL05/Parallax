import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useAuth } from "@clerk/clerk-react";
import { Download, Lock, ArrowLeft } from "lucide-react";
import TimelineChart from "./TimelineChart";
import { premiumService, SubscriptionAnalytics } from "../services/premiumService";
import { stripeService } from "../services/stripeService";
import type { SimulationResult } from "../types/api";

interface SimulationResultsProps {
  simulation: SimulationResult;
  onNewSimulation: () => void;
}

const SimulationResults: React.FC<SimulationResultsProps> = ({ simulation, onNewSimulation }) => {
  const { getToken, isSignedIn } = useAuth();
  const [sub, setSub] = useState<SubscriptionAnalytics | null>(null);
  const [loadingSub, setLoadingSub] = useState(true);

  useEffect(() => {
    if (isSignedIn) {
      getToken().then(token => {
        if (token) premiumService.getSubscriptionStatus(token).then(setSub).catch(() => {});
      }).finally(() => setLoadingSub(false));
    } else {
      setLoadingSub(false);
    }
  }, [isSignedIn]);

  const isPremium = sub?.subscription.tier === "premium" && sub?.subscription.is_active;

  const handleExport = async (format: "json" | "pdf" | "csv" | "excel") => {
    if (!isPremium && format !== "json") return;
    try {
      const token = await getToken();
      if (!token) return;
      const blob = await premiumService.exportSimulation(token, { simulation_id: simulation.id, format });
      const a = document.createElement("a");
      a.href = window.URL.createObjectURL(blob);
      a.download = `simulation.${format}`;
      a.click();
    } catch (e) { console.error("Export failed:", e); }
  };

  const handleUpgrade = async () => {
    try {
      const token = await getToken();
      const co = await stripeService.createCheckoutSession("premium_monthly", token || undefined);
      if (co.url) window.location.href = co.url;
    } catch (e) { console.error(e); }
  };

  const last = (tl: typeof simulation.choice_a_timeline) => tl[tl.length - 1];
  const first = (tl: typeof simulation.choice_a_timeline) => tl[0];
  const avgH = (tl: typeof simulation.choice_a_timeline) =>
    (tl.reduce((s, p) => s + p.happiness_score, 0) / tl.length).toFixed(1);
  const growth = (tl: typeof simulation.choice_a_timeline) => {
    const f = first(tl)?.salary || 1;
    return Math.round(((last(tl)?.salary || 0) - f) / f * 100);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
      {/* Nav */}
      <button onClick={onNewSimulation} className="inline-flex items-center gap-1 text-sm text-stone-400 hover:text-stone-900 transition-colors mb-8">
        <ArrowLeft size={14} /> Back
      </button>

      <h2 className="text-3xl sm:text-4xl font-bold text-stone-900 mb-2">Results</h2>
      <p className="text-stone-400 text-sm mb-10">10-year projection for each path</p>

      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-stone-200 rounded-xl overflow-hidden mb-10">
        <Metric label="Path A final salary" value={`$${last(simulation.choice_a_timeline)?.salary?.toLocaleString() || "—"}`} sub={`+${growth(simulation.choice_a_timeline)}%`} />
        <Metric label="Path B final salary" value={`$${last(simulation.choice_b_timeline)?.salary?.toLocaleString() || "—"}`} sub={`+${growth(simulation.choice_b_timeline)}%`} />
        <Metric label="Path A happiness" value={`${avgH(simulation.choice_a_timeline)}/10`} sub={last(simulation.choice_a_timeline)?.career_title || ""} />
        <Metric label="Path B happiness" value={`${avgH(simulation.choice_b_timeline)}/10`} sub={last(simulation.choice_b_timeline)?.career_title || ""} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-10">
        <motion.div className="bg-white rounded-xl border border-stone-200 p-5"
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            <span className="text-xs tracking-widest uppercase text-stone-400">Path A</span>
          </div>
          <TimelineChart data={simulation.choice_a_timeline} title="PathA" color="#3b82f6" />
        </motion.div>
        <motion.div className="bg-white rounded-xl border border-stone-200 p-5"
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-xs tracking-widest uppercase text-stone-400">Path B</span>
          </div>
          <TimelineChart data={simulation.choice_b_timeline} title="PathB" color="#10b981" />
        </motion.div>
      </div>

      {/* Summary */}
      <div className="bg-white rounded-xl border border-stone-200 p-6 sm:p-8 mb-10">
        <p className="text-xs tracking-widest uppercase text-stone-400 mb-3">Analysis</p>
        <p className="text-stone-700 text-[15px] leading-relaxed">{simulation.summary}</p>
      </div>

      {/* Export row */}
      <div className="flex flex-wrap items-center gap-2 mb-10">
        <span className="text-xs text-stone-400 mr-2">Export</span>
        <button onClick={() => handleExport("json")}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs border border-stone-200 rounded-lg hover:border-stone-400 transition-colors">
          <Download size={12} /> JSON
        </button>
        {isPremium ? (
          (["pdf", "csv", "excel"] as const).map(f => (
            <button key={f} onClick={() => handleExport(f)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs border border-stone-200 rounded-lg hover:border-stone-400 transition-colors">
              <Download size={12} /> {f.toUpperCase()}
            </button>
          ))
        ) : (
          <button onClick={handleUpgrade}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs text-stone-500 border border-stone-200 rounded-lg hover:border-stone-400 transition-colors">
            <Lock size={12} /> More formats
          </button>
        )}
      </div>

      {/* Upsell */}
      {!loadingSub && !isPremium && (
        <div className="bg-stone-950 rounded-xl p-6 sm:p-8 mb-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-white font-medium mb-1">Want risk assessments and market analysis?</p>
            <p className="text-stone-500 text-sm">Upgrade to Premium for deeper insights on every simulation.</p>
          </div>
          <button onClick={handleUpgrade}
            className="flex-shrink-0 px-5 py-2.5 bg-white text-stone-900 text-sm font-medium rounded-xl hover:bg-stone-100 transition-colors">
            Upgrade
          </button>
        </div>
      )}

      <div className="text-center">
        <button onClick={onNewSimulation}
          className="px-6 py-3 bg-stone-950 text-white text-sm font-medium rounded-xl hover:bg-stone-800 transition-colors">
          New simulation
        </button>
      </div>
    </motion.div>
  );
};

const Metric: React.FC<{ label: string; value: string; sub: string }> = ({ label, value, sub }) => (
  <div className="bg-white p-5">
    <p className="text-xs text-stone-400 mb-2">{label}</p>
    <p className="text-xl font-semibold text-stone-900">{value}</p>
    <p className="text-xs text-stone-400 mt-1 truncate">{sub}</p>
  </div>
);

export default SimulationResults;
