import React from 'react';
import { motion } from 'framer-motion';

const FeaturesSection: React.FC = () => {
  return (
    <section id="features" className="py-20 bg-white">
      <div className="max-w-5xl mx-auto px-5">
        <motion.p
          className="text-accent-600 text-sm tracking-[0.2em] uppercase mb-3 font-medium"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          What you get
        </motion.p>
        <motion.h2
          className="font-display text-3xl sm:text-4xl text-stone-900 mb-14 max-w-lg"
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          Not another prediction tool.{' '}
          <span className="italic">A decision engine.</span>
        </motion.h2>

        {/* Bento grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Large card — left */}
          <motion.div
            className="md:col-span-2 bg-stone-950 text-white rounded-2xl p-8 sm:p-10 flex flex-col justify-between min-h-[280px] grain relative overflow-hidden"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
          >
            <div>
              <p className="text-accent-400 text-xs tracking-[0.2em] uppercase mb-4 font-medium">Core engine</p>
              <h3 className="text-2xl font-semibold mb-3 font-display">ML-driven salary predictions</h3>
              <p className="text-stone-400 text-sm leading-relaxed max-w-md">
                XGBoost models trained on 15,000+ data points across 89 professions.
                Not generic estimates — real salary ranges by position level, education, location, and industry.
              </p>
            </div>
            {/* Mini chart mockup */}
            <div className="flex items-end gap-1.5 mt-8 h-14">
              {[30, 35, 42, 48, 45, 55, 62, 68, 75, 85].map((h, i) => (
                <motion.div
                  key={i}
                  className="flex-1 bg-accent-400/20 rounded-sm"
                  initial={{ height: 0 }}
                  whileInView={{ height: `${h}%` }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: 0.3 + i * 0.05 }}
                />
              ))}
            </div>
          </motion.div>

          {/* Small card — right top */}
          <motion.div
            className="bg-stone-50 rounded-2xl p-8 flex flex-col justify-between min-h-[280px] border border-stone-200/60 shadow-elevated hover:shadow-card transition-shadow duration-300"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <div>
              <p className="text-accent-600 text-xs tracking-[0.2em] uppercase mb-4 font-medium">Validation</p>
              <h3 className="text-lg font-semibold text-stone-900 mb-2">AI cross-checks</h3>
              <p className="text-stone-500 text-sm leading-relaxed">
                LLM-generated narratives validated against ML predictions. If the AI hallucinates a salary, the model corrects it.
              </p>
            </div>
            <div className="text-4xl font-display text-stone-300 mt-6">±5%</div>
          </motion.div>

          {/* Small card — bottom left */}
          <motion.div
            className="bg-stone-50 rounded-2xl p-8 min-h-[200px] border border-stone-200/60 shadow-elevated hover:shadow-card transition-shadow duration-300"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.15 }}
          >
            <p className="text-accent-600 text-xs tracking-[0.2em] uppercase mb-4 font-medium">Coverage</p>
            <h3 className="text-lg font-semibold text-stone-900 mb-2">Training careers</h3>
            <p className="text-stone-500 text-sm leading-relaxed">
              Doctors, surgeons, and other training professions model residency periods with accurate salary jumps post-training.
            </p>
          </motion.div>

          {/* Medium card — bottom right */}
          <motion.div
            className="md:col-span-2 bg-stone-50 rounded-2xl p-8 min-h-[200px] border border-stone-200/60 shadow-elevated hover:shadow-card transition-shadow duration-300"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <p className="text-accent-600 text-xs tracking-[0.2em] uppercase mb-4 font-medium">Dimensions</p>
            <h3 className="text-lg font-semibold text-stone-900 mb-3">More than salary</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 mt-6">
              {[
                { label: "Salary growth", detail: "Year over year" },
                { label: "Happiness", detail: "1–10 scale" },
                { label: "Career stability", detail: "Industry-adjusted" },
                { label: "Life events", detail: "Promotions, changes" },
              ].map((d, i) => (
                <div key={i} className="border-l-2 border-accent-200 pl-3">
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
