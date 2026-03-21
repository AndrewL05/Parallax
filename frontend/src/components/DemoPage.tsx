import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, FlaskConical } from "lucide-react";
import SimulationResults from "./SimulationResults";
import { simulationService } from "../services/simulationService";
import type { SimulationResult } from "../types/api";

const DemoPage: React.FC = () => {
  const navigate = useNavigate();
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    simulationService
      .getDemoSimulation()
      .then(setSimulation)
      .catch(() => setError("Demo simulation not available. Please try again later."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="pt-20 pb-20 min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-6 h-6 border-2 border-stone-300 border-t-stone-900 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-stone-400 text-sm">Loading demo...</p>
        </div>
      </div>
    );
  }

  if (error || !simulation) {
    return (
      <div className="pt-20 pb-20 min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-stone-500 text-sm mb-4">{error || "Demo not available."}</p>
          <button onClick={() => navigate("/")} className="text-sm text-stone-900 underline underline-offset-2 hover:text-stone-600">
            Back to home
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      key="demo"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className="pt-20 pb-20 min-h-screen bg-stone-50"
    >
      <div className="max-w-5xl mx-auto px-5">
        <button
          onClick={() => navigate("/")}
          className="inline-flex items-center gap-1 text-sm text-stone-400 hover:text-stone-900 transition-colors mb-8"
        >
          <ArrowLeft size={14} /> Back
        </button>

        <motion.div
          className="relative overflow-hidden rounded-2xl bg-stone-950 p-6 sm:p-10 mb-12"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="absolute inset-0 grain pointer-events-none" />

          <div
            className="absolute top-0 right-0 w-[400px] h-[300px] opacity-[0.08] pointer-events-none"
            style={{
              background:
                "radial-gradient(ellipse at top right, rgba(236,154,12,0.5) 0%, transparent 70%)",
            }}
          />

          <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-accent-400/10 flex items-center justify-center">
              <FlaskConical size={20} className="text-accent-400" />
            </div>
            <div className="flex-1">
              <h1 className="font-display text-2xl sm:text-3xl text-white italic tracking-tight mb-1">
                Demo results
              </h1>
              <p className="text-stone-500 text-sm leading-relaxed max-w-xl">
                Physician vs. Lawyer — a sample 10-year simulation showing how
                Parallax models salary trajectories, happiness scores, and
                career milestones for each path.
              </p>
            </div>
            <motion.button
              onClick={() => {
                navigate("/");
                setTimeout(() => {
                  document
                    .getElementById("simulator")
                    ?.scrollIntoView({ behavior: "smooth" });
                }, 150);
              }}
              className="flex-shrink-0 px-5 py-2.5 bg-white text-stone-900 text-sm font-medium rounded-xl hover:bg-stone-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-400 active:bg-stone-200 transition-colors"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              Run your own
            </motion.button>
          </div>
        </motion.div>

        <SimulationResults
          simulation={simulation}
          onNewSimulation={() => navigate("/")}
        />
      </div>
    </motion.div>
  );
};

export default DemoPage;
