import React from 'react';
import { motion } from 'framer-motion';

interface Feature {
  icon: string;
  title: string;
  description: string;
  image: string;
}

const FeaturesSection: React.FC = () => {
  const features: Feature[] = [
    {
      icon: '🤖',
      title: 'AI-Powered Predictions',
      description: 'Advanced AI analyzes countless factors to generate realistic life projections based on your choices.',
      image: 'https://images.unsplash.com/photo-1549057446-3e7efef87383'
    },
    {
      icon: '📊',
      title: 'Interactive Visualizations',
      description: 'Beautiful charts and timelines that make complex data easy to understand and explore.',
      image: 'https://images.unsplash.com/photo-1539992190939-08f22d7ebaad'
    },
    {
      icon: '🎯',
      title: 'Personalized Insights',
      description: 'Get tailored analysis based on your age, location, education, and current situation.',
      image: 'https://images.pexels.com/photos/4220084/pexels-photo-4220084.jpeg'
    }
  ];

  return (
    <section id="features" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl font-bold text-gray-800 mb-6">
            Powerful Features
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Everything you need to make informed life decisions with confidence
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              className="bg-white rounded-2xl shadow-xl overflow-hidden hover:shadow-2xl transition-all duration-300 hover:scale-105"
            >
              <div className="h-48 overflow-hidden">
                <img
                  src={feature.image}
                  alt={feature.title}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="p-8">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-2xl font-bold text-gray-800 mb-4">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;