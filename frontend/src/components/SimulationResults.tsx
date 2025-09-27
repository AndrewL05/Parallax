import React from 'react';
import { motion } from 'framer-motion';
import TimelineChart from './TimelineChart';
import type { SimulationResult } from '../types/api';

interface SimulationResultsProps {
  simulation: SimulationResult;
  onNewSimulation: () => void;
}

const SimulationResults: React.FC<SimulationResultsProps> = ({ simulation, onNewSimulation }) => {
  const getLastTimelinePoint = (timeline: typeof simulation.choice_a_timeline) => {
    return timeline[timeline.length - 1];
  };

  const calculateAverageHappiness = (timeline: typeof simulation.choice_a_timeline): number => {
    const sum = timeline.reduce((acc, point) => acc + point.happiness_score, 0);
    return sum / timeline.length;
  };

  return (
    <motion.div
      className="max-w-7xl mx-auto"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-gray-800 mb-4">Your Life Simulation Results</h2>
        <p className="text-gray-600 text-lg">Compare how your two life paths might unfold over the next 10 years</p>
      </div>

      {/* Timeline Visualizations */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
        <motion.div
          className="bg-white rounded-2xl shadow-xl p-6"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <TimelineChart
            data={simulation.choice_a_timeline}
            title="Path A Timeline"
            color="#2563EB"
          />
        </motion.div>

        <motion.div
          className="bg-white rounded-2xl shadow-xl p-6"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <TimelineChart
            data={simulation.choice_b_timeline}
            title="Path B Timeline"
            color="#059669"
          />
        </motion.div>
      </div>

      {/* Summary */}
      <motion.div
        className="bg-white rounded-2xl shadow-xl p-8 mb-8"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <h3 className="text-2xl font-bold text-gray-800 mb-4">AI Analysis & Insights</h3>
        <p className="text-gray-700 leading-relaxed text-lg">{simulation.summary}</p>
      </motion.div>

      {/* Quick Stats Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Path A Stats */}
        <motion.div
          className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <h4 className="text-xl font-bold text-blue-800 mb-4">Path A Highlights</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-blue-700">10-Year Salary:</span>
              <span className="font-semibold">
                ${getLastTimelinePoint(simulation.choice_a_timeline)?.salary?.toLocaleString() || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Avg Happiness:</span>
              <span className="font-semibold">
                {calculateAverageHappiness(simulation.choice_a_timeline).toFixed(1)}/10
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Final Role:</span>
              <span className="font-semibold">
                {getLastTimelinePoint(simulation.choice_a_timeline)?.career_title || 'N/A'}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Path B Stats */}
        <motion.div
          className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 1.0 }}
        >
          <h4 className="text-xl font-bold text-green-800 mb-4">Path B Highlights</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-green-700">10-Year Salary:</span>
              <span className="font-semibold">
                ${getLastTimelinePoint(simulation.choice_b_timeline)?.salary?.toLocaleString() || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Avg Happiness:</span>
              <span className="font-semibold">
                {calculateAverageHappiness(simulation.choice_b_timeline).toFixed(1)}/10
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Final Role:</span>
              <span className="font-semibold">
                {getLastTimelinePoint(simulation.choice_b_timeline)?.career_title || 'N/A'}
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="text-center">
        <motion.button
          onClick={onNewSimulation}
          className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-3 px-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Create New Simulation
        </motion.button>
      </div>
    </motion.div>
  );
};

export default SimulationResults;