import React, { useState } from "react";
import { ClerkProvider } from "@clerk/clerk-react";
import { motion, AnimatePresence } from "framer-motion";
import "./App.css";

// Components
import Navigation from "./components/Navigation";
import HeroSection from "./components/Hero";
import FeaturesSection from "./components/Features";
import HowItWorksSection from "./components/HowItWorks";
import PricingSection from "./components/Pricing";
import FooterSection from "./components/Footer";
import LifeChoiceForm from "./components/LifeChoiceForm";
import SimulationResults from "./components/SimulationResults";

// Hooks
import { useAuth } from "./hooks/useAuth";
import { useSimulation } from "./hooks/useSimulation";

const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

// Main App Content Component
const AppContent = () => {
  const [currentView, setCurrentView] = useState("home");
  const { isSignedIn } = useAuth();
  const { simulation, isLoading, createSimulation, resetSimulation } =
    useSimulation();

  const handleSimulationSubmit = async (formData) => {
    try {
      await createSimulation(formData);
      setCurrentView("results");
    } catch (error) {
      console.error("Simulation failed:", error);
      alert("Failed to generate simulation. Please try again.");
    }
  };

  const handleNewSimulation = () => {
    resetSimulation();
    setCurrentView("home");
  };

  const handleLogoClick = () => {
    resetSimulation();
    setCurrentView("home");
  };

  return (
    <div className="min-h-screen">
      <Navigation onLogoClick={handleLogoClick} />

      <main>
        <AnimatePresence mode="wait">
          {currentView === "home" && (
            <motion.div
              key="home"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <HeroSection />
              <FeaturesSection />
              <HowItWorksSection />

              {/* Simulator Section */}
              <section
                id="simulator"
                className="py-20 bg-gradient-to-br from-purple-100 via-blue-50 to-indigo-100"
              >
                <div className="container mx-auto px-4">
                  <div className="text-center mb-12">
                    <motion.h2
                      className="text-5xl md:text-6xl font-bold text-gray-800 mb-6"
                      initial={{ opacity: 0, y: -30 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.8 }}
                    >
                      Try It Now
                    </motion.h2>
                    <motion.p
                      className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
                      initial={{ opacity: 0, y: 30 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.8, delay: 0.2 }}
                    >
                      Start exploring your future possibilities with our
                      AI-powered life simulator
                    </motion.p>
                  </div>

                  <LifeChoiceForm
                    onSubmit={handleSimulationSubmit}
                    isLoading={isLoading}
                  />
                </div>
              </section>

              <PricingSection />
              <FooterSection />
            </motion.div>
          )}

          {currentView === "results" && simulation && (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="pt-20 pb-20 bg-gradient-to-br from-purple-100 via-blue-50 to-indigo-100"
            >
              <div className="container mx-auto px-4">
                <SimulationResults
                  simulation={simulation}
                  onNewSimulation={handleNewSimulation}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

// Main App Component
function App() {
  if (!CLERK_PUBLISHABLE_KEY) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-red-600">Missing Clerk publishable key</p>
      </div>
    );
  }

  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <AppContent />
    </ClerkProvider>
  );
}

export default App;
