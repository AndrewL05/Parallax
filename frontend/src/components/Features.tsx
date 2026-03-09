import React from 'react';
import { motion } from 'framer-motion';

const FeaturesSection: React.FC = () => {
  return (
    <section id="features" className="py-24 bg-white border-t border-stone-100">
      <div className="max-w-5xl mx-auto px-5">
        <motion.p
          className="text-stone-400 text-sm tracking-widest uppercase mb-3"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          What you get
        </motion.p>
        <motion.h2
          className="text-3xl sm:text-4xl font-bold text-stone-900 mb-16 max-w-lg"
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          Not another prediction tool. A decision engine.
        </motion.h2>

        {/* Bento grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Large card — left */}
          <motion.div
            className="md:col-span-2 bg-stone-950 text-white rounded-2xl p-8 sm:p-10 flex flex-col justify-between min-h-[280px]"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
          >
            <div>
              <p className="text-stone-500 text-xs tracking-widest uppercase mb-4">Core engine</p>
              <h3 className="text-2xl font-semibold mb-3">ML-driven salary predictions</h3>
              <p className="text-stone-400 text-sm leading-relaxed max-w-md">
                XGBoost models trained on 15,000+ data points across 89 professions.
                Not generic estimates — real salary ranges by position level, education, location, and industry.
              </p>
            </div>
            {/* Mini chart mockup */}
            <div className="flex items-end gap-1 mt-8 h-12">
              {[30, 35, 42, 48, 45, 55, 62, 68, 75, 85].map((h, i) => (
                <div key={i} className="flex-1 bg-white/10 rounded-sm" style={{ height: `${h}%` }} />
              ))}
            </div>
          </motion.div>

          {/* Small card — right top */}
          <motion.div
            className="bg-stone-50 rounded-2xl p-8 flex flex-col justify-between min-h-[280px]"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <div>
              <p className="text-stone-400 text-xs tracking-widest uppercase mb-4">Validation</p>
              <h3 className="text-lg font-semibold text-stone-900 mb-2">AI cross-checks</h3>
              <p className="text-stone-500 text-sm leading-relaxed">
                LLM-generated narratives validated against ML predictions. If the AI hallucinates a salary, the model corrects it.
              </p>
            </div>
            <div className="text-4xl font-bold text-stone-300 mt-6">±5%</div>
          </motion.div>

          {/* Small card — bottom left */}
          <motion.div
            className="bg-stone-50 rounded-2xl p-8 min-h-[200px]"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.15 }}
          >
            <p className="text-stone-400 text-xs tracking-widest uppercase mb-4">Coverage</p>
            <h3 className="text-lg font-semibold text-stone-900 mb-2">Training careers</h3>
            <p className="text-stone-500 text-sm leading-relaxed">
              Doctors, surgeons, and other training professions model residency periods with accurate salary jumps post-training.
            </p>
          </motion.div>

          {/* Medium card — bottom right */}
          <motion.div
            className="md:col-span-2 bg-stone-50 rounded-2xl p-8 min-h-[200px]"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <p className="text-stone-400 text-xs tracking-widest uppercase mb-4">Dimensions</p>
            <h3 className="text-lg font-semibold text-stone-900 mb-3">More than salary</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
              {[
                { label: "Salary growth", detail: "Year over year" },
                { label: "Happiness", detail: "1–10 scale" },
                { label: "Career stability", detail: "Industry-adjusted" },
                { label: "Life events", detail: "Promotions, changes" },
              ].map((d, i) => (
                <div key={i}>
                  <div className="text-sm font-medium text-stone-900">{d.label}</div>
                  <div className="text-xs text-stone-400 mt-0.5">{d.detail}</div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
