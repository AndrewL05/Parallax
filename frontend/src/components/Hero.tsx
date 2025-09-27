import React from "react";
import { motion } from "framer-motion";

const HeroSection: React.FC = () => {
  const handleScrollToSimulator = (): void => {
    const simulatorElement = document.getElementById("simulator");
    if (simulatorElement) {
      simulatorElement.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-white via-purple-50/30 to-blue-50/50 overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-96 h-96 bg-gradient-to-r from-purple-200/40 to-blue-200/40 rounded-full opacity-60 blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-80 h-80 bg-gradient-to-r from-blue-200/40 to-indigo-200/40 rounded-full opacity-60 blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-gradient-to-r from-pink-200/30 to-purple-200/30 rounded-full opacity-40 blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="relative z-10 text-center max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-20"
        >
          <motion.h1
            className="text-6xl md:text-8xl font-bold text-gray-900 mb-8 mt-10 leading-tight"
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            Explore Your
            <motion.span
              className="bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent block"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{
                duration: 1,
                delay: 0.5,
                type: "spring",
                stiffness: 100,
              }}
            >
              Future Paths
            </motion.span>
          </motion.h1>

          <motion.p
            className="text-xl md:text-2xl text-gray-600 mb-12 max-w-4xl mx-auto leading-relaxed font-light"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            AI-powered life simulation that helps you visualize the long-term
            outcomes of major decisions. Compare career changes, relocations,
            and life choices with data-driven insights.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <motion.button
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-4 px-8 rounded-2xl text-lg shadow-2xl hover:shadow-purple-500/25 transition-all duration-300 transform hover:-translate-y-1"
              whileHover={{
                scale: 1.05,
                boxShadow:
                  "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
              }}
              whileTap={{ scale: 0.95 }}
              onClick={handleScrollToSimulator}
            >
              Start Your Simulation
            </motion.button>

            <motion.button
              className="bg-white/70 backdrop-blur-sm border-2 border-gray-300 text-gray-700 hover:bg-white hover:border-gray-400 font-bold py-4 px-8 rounded-2xl text-lg transition-all duration-300 shadow-lg hover:shadow-xl"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Watch Demo
            </motion.button>
          </motion.div>
        </motion.div>

        {/* Example Simulations */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto"
        >
          {/* Career Change Simulation */}
          <motion.div
            className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 text-left border border-white/20 hover:bg-white/90 transition-all duration-300"
            whileHover={{ scale: 1.02, y: -5 }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex items-center mb-4">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
              <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Career Change Simulation
              </h3>
            </div>
            <p className="text-gray-600 mb-6 italic text-lg">
              "Should I switch from marketing to software engineering?"
            </p>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl">
                <span className="text-gray-700 font-medium">
                  5-year salary projection:
                </span>
                <span className="text-green-600 font-bold text-lg">+127%</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-50 to-sky-50 rounded-xl">
                <span className="text-gray-700 font-medium">
                  Happiness score:
                </span>
                <span className="text-blue-600 font-bold text-lg">8.2/10</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl">
                <span className="text-gray-700 font-medium">
                  Career stability:
                </span>
                <span className="text-green-600 font-bold text-lg">High</span>
              </div>
            </div>
          </motion.div>

          {/* Relocation Analysis */}
          <motion.div
            className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 text-left border border-white/20 hover:bg-white/90 transition-all duration-300"
            whileHover={{ scale: 1.02, y: -5 }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex items-center mb-4">
              <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
              <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Relocation Analysis
              </h3>
            </div>
            <p className="text-gray-600 mb-6 italic text-lg">
              "Moving from Denver to Austin for better opportunities"
            </p>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl">
                <span className="text-gray-700 font-medium">
                  Cost of living impact:
                </span>
                <span className="text-orange-600 font-bold text-lg">+15%</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-purple-50 to-violet-50 rounded-xl">
                <span className="text-gray-700 font-medium">
                  Network growth:
                </span>
                <span className="text-purple-600 font-bold text-lg">
                  Strong
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-50 to-sky-50 rounded-xl">
                <span className="text-gray-700 font-medium">
                  Quality of life:
                </span>
                <span className="text-blue-600 font-bold text-lg">9.1/10</span>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;