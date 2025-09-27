import React from 'react';
import { motion } from 'framer-motion';

interface Step {
  number: string;
  title: string;
  description: string;
  icon: string;
}

const HowItWorksSection: React.FC = () => {
  const steps: Step[] = [
    {
      number: '1',
      title: 'Define Your Choices',
      description: 'Input two different life paths you\'re considering, with detailed descriptions and context.',
      icon: '✏️'
    },
    {
      number: '2',
      title: 'AI Analysis',
      description: 'Our advanced AI analyzes your options and generates realistic 10-year projections.',
      icon: '🧠'
    },
    {
      number: '3',
      title: 'Explore Results',
      description: 'Visualize and compare timelines showing salary, happiness, and major life events.',
      icon: '📈'
    },
    {
      number: '4',
      title: 'Make Decisions',
      description: 'Use insights to make informed choices about your future with confidence.',
      icon: '🎯'
    }
  ];

  return (
    <section id="how-it-works" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl font-bold text-gray-800 mb-6">
            How It Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Simple steps to unlock insights about your future
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              className="text-center"
            >
              <div className="relative mb-6">
                <div className="w-20 h-20 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4 shadow-lg">
                  {step.number}
                </div>
                <div className="text-4xl mb-4">{step.icon}</div>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-4">{step.title}</h3>
              <p className="text-gray-600 leading-relaxed">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;