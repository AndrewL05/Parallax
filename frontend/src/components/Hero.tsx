import React from "react";
import { motion } from "framer-motion";

const HeroSection: React.FC = () => {
  const scrollToSimulator = () => {
    document.getElementById("simulator")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center bg-stone-950 overflow-hidden">
      {/* Diverging paths — the visual identity */}
      <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
        <line x1="50%" y1="15%" x2="25%" y2="95%" stroke="rgba(255,255,255,0.04)" strokeWidth="1" />
        <line x1="50%" y1="15%" x2="75%" y2="95%" stroke="rgba(255,255,255,0.04)" strokeWidth="1" />
        <line x1="50%" y1="15%" x2="20%" y2="95%" stroke="rgba(255,255,255,0.02)" strokeWidth="1" />
        <line x1="50%" y1="15%" x2="80%" y2="95%" stroke="rgba(255,255,255,0.02)" strokeWidth="1" />
      </svg>

      <div className="relative z-10 max-w-3xl mx-auto px-5 text-center">
        <motion.p
          className="text-stone-500 text-sm tracking-widest uppercase mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          Life simulation engine
        </motion.p>

        <motion.h1
          className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white leading-[1.05] tracking-tight mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
        >
          Two paths.
          <br />
          <span className="text-stone-500">One future.</span>
        </motion.h1>

        <motion.p
          className="text-stone-400 text-lg sm:text-xl leading-relaxed max-w-xl mx-auto mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
        >
          Enter two life decisions. Get a 10-year projection for each —
          salary, happiness, career milestones — powered by ML models
          trained on real profession data.
        </motion.p>

        <motion.button
          onClick={scrollToSimulator}
          className="px-8 py-3.5 bg-white text-stone-900 text-sm font-medium rounded-xl hover:bg-stone-100 transition-colors"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Try it now
        </motion.button>

        {/* Metrics — not a feature grid, just proof points */}
        <motion.div
          className="flex items-center justify-center gap-8 sm:gap-12 mt-20 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          {[
            { value: "89+", label: "professions" },
            { value: "10yr", label: "projections" },
            { value: "R² .91", label: "model accuracy" },
          ].map((m, i) => (
            <div key={i} className="text-center">
              <div className="text-white font-semibold text-lg">{m.value}</div>
              <div className="text-stone-600 text-xs tracking-wide">{m.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;
