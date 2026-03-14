import React, { useState, useEffect } from "react";
import { ClerkProvider } from "@clerk/clerk-react";
import { motion, AnimatePresence } from "framer-motion";
import "./App.css";

import Navigation from "./components/Navigation";
import HeroSection from "./components/Hero";
import FeaturesSection from "./components/Features";
import HowItWorksSection from "./components/HowItWorks";
import PricingSection from "./components/Pricing";
import FooterSection from "./components/Footer";
import LifeChoiceForm from "./components/LifeChoiceForm";
import SimulationResults from "./components/SimulationResults";
import SubscriptionStatus from "./components/SubscriptionStatus";

import { useAuth } from "./hooks/useAuth";
import { useSimulation } from "./hooks/useSimulation";

import type { SimulationFormData } from "./types/simulation";

const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

type ViewType = "home" | "results" | "subscription";

const AppContent: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewType>(() => {
    // handle Stripe redirect: /success → show subscription page
    if (window.location.pathname === "/success") {
      window.history.replaceState({}, "", "/");
      return "subscription";
    }
    return "home";
  });
  const {} = useAuth();
  const { simulation, isLoading, createSimulation, resetSimulation, setSimulation } = useSimulation();

  const handleSimulationSubmit = async (formData: SimulationFormData): Promise<void> => {
    try {
      await createSimulation(formData);
      setCurrentView("results");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
      console.error("Simulation failed:", error);
      let msg = "Failed to generate simulation. Please try again.";
      if (error instanceof Error) {
        if (error.message.includes("401") || error.message.toLowerCase().includes("sign in")) {
          msg = "Please sign in to run a simulation.";
        }
      }
      alert(msg);
    }
  };

  const handleNewSimulation = () => { resetSimulation(); setCurrentView("home"); };
  const handleLogoClick = () => { resetSimulation(); setCurrentView("home"); };
  const handleViewSimulation = (sim: import("./types/api").SimulationResult) => {
    setSimulation(sim);
    setCurrentView("results");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen">
      <Navigation onLogoClick={handleLogoClick} onSubscriptionClick={() => setCurrentView("subscription")} />

      <main>
        <AnimatePresence mode="wait">
          {currentView === "home" && (
            <motion.div key="home" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>
              <HeroSection />
              <FeaturesSection />
              <HowItWorksSection />
              <section id="simulator" className="py-20 bg-stone-100/50 border-y border-stone-200/60">
                <div className="max-w-5xl mx-auto px-5">
                  <LifeChoiceForm onSubmit={handleSimulationSubmit} isLoading={isLoading} />
                </div>
              </section>
              <PricingSection />
              <FooterSection />
            </motion.div>
          )}

          {currentView === "results" && simulation && (
            <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}
              className="pt-20 pb-20 min-h-screen bg-stone-50">
              <div className="max-w-5xl mx-auto px-5">
                <SimulationResults simulation={simulation} onNewSimulation={handleNewSimulation} />
              </div>
            </motion.div>
          )}

          {currentView === "subscription" && (
            <motion.div key="subscription" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}
              className="pt-20 pb-20 min-h-screen bg-stone-50">
              <div className="max-w-5xl mx-auto px-5">
                <SubscriptionStatus onViewSimulation={handleViewSimulation} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

const App: React.FC = () => {
  if (!CLERK_PUBLISHABLE_KEY) {
    return <div className="flex items-center justify-center min-h-screen"><p className="text-red-600 text-sm">Missing Clerk publishable key</p></div>;
  }
  return <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}><AppContent /></ClerkProvider>;
};

export default App;
