import React from 'react';
import { motion } from 'framer-motion';

const HowItWorksSection: React.FC = () => {
  const steps = [
    { num: "01", title: "Define your paths", text: "Describe two life paths you're weighing — careers, cities, degrees, anything." },
    { num: "02", title: "ML projects 10 years", text: "Our models simulate salary, happiness, and milestones for each path." },
    { num: "03", title: "Compare & decide", text: "See side-by-side projections with charts, narratives, and key metrics." },
  ];

  return (
    <section id="how-it-works" className="py-16 bg-white">
      <div className="max-w-5xl mx-auto px-5">
        <motion.p
          className="text-accent-600 text-sm tracking-[0.2em] uppercase mb-3 font-medium"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          How it works
        </motion.p>
        <motion.h2
          className="font-display text-3xl sm:text-4xl text-stone-900 mb-12"
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          Three steps to clarity.
        </motion.h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, i) => (
            <motion.div
              key={i}
              className="relative pl-6 border-l-2 border-accent-200"
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
            >
              <span className="text-accent-400 text-sm font-mono font-semibold">{step.num}</span>
              <h3 className="text-stone-900 font-semibold mt-1 mb-2">{step.title}</h3>
              <p className="text-stone-500 text-sm leading-relaxed">{step.text}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
