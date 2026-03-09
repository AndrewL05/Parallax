import React from 'react';
import { motion } from 'framer-motion';

const HowItWorksSection: React.FC = () => {
  const steps = [
    { num: "01", text: "Describe two life paths you're weighing" },
    { num: "02", text: "Our ML model projects 10 years for each" },
    { num: "03", text: "Compare salary, happiness, and milestones" },
  ];

  return (
    <section id="how-it-works" className="py-20 bg-white">
      <div className="max-w-5xl mx-auto px-5">
        <div className="border-t border-stone-200 pt-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
              >
                <span className="text-stone-300 text-sm font-mono">{step.num}</span>
                <p className="text-stone-800 text-[15px] leading-relaxed mt-2">{step.text}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
