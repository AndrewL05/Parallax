import React from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

const HeroSection: React.FC = () => {
  const navigate = useNavigate();
  const scrollToSimulator = () => {
    document.getElementById("simulator")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center bg-stone-950 overflow-hidden grain">
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-gradient-radial rounded-full opacity-[0.07]"
        style={{ background: 'radial-gradient(ellipse at center, rgba(236,154,12,0.3) 0%, transparent 70%)' }} />

      <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
        <line x1="50%" y1="12%" x2="22%" y2="98%" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
        <line x1="50%" y1="12%" x2="78%" y2="98%" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
        <line x1="50%" y1="12%" x2="18%" y2="98%" stroke="rgba(255,255,255,0.025)" strokeWidth="1" />
        <line x1="50%" y1="12%" x2="82%" y2="98%" stroke="rgba(255,255,255,0.025)" strokeWidth="1" />
        <circle cx="50%" cy="12%" r="2" fill="rgba(236,154,12,0.3)" />
      </svg>

      <div className="relative z-10 max-w-3xl mx-auto px-5 text-center">
        <motion.p
          className="text-stone-500 text-sm tracking-[0.2em] uppercase mb-8 font-medium"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          Life simulation engine
        </motion.p>

        <motion.h1
          className="font-display text-5xl sm:text-6xl lg:text-7xl text-white leading-[1.05] tracking-tight mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
        >
          Two paths.
          <br />
          <span className="text-accent-400 italic">One future.</span>
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
          className="px-10 py-4 bg-white text-stone-900 text-sm font-semibold rounded-full hover:bg-stone-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-400 focus-visible:ring-offset-2 focus-visible:ring-offset-stone-950 active:bg-stone-200 transition-colors"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
        >
          Try it now
        </motion.button>

        <motion.button
          onClick={() => { navigate("/demo"); window.scrollTo({ top: 0, behavior: "smooth" }); }}
          className="ml-4 px-8 py-4 border border-white/25 text-white/80 text-sm font-medium rounded-full hover:border-white/50 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-400 focus-visible:ring-offset-2 focus-visible:ring-offset-stone-950 active:bg-white/5 transition-colors"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
        >
          View demo
        </motion.button>

        <motion.div
          className="flex items-center justify-center gap-10 sm:gap-16 mt-20"
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
              <div className="text-white font-semibold text-xl tracking-tight">{m.value}</div>
              <div className="text-stone-500 text-xs tracking-wide mt-1">{m.label}</div>
            </div>
          ))}
        </motion.div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-white to-transparent" />
    </section>
  );
};

export default HeroSection;
