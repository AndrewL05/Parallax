import React, { useState, useEffect } from "react";
import { ClerkProvider } from "@clerk/clerk-react";
import { BrowserRouter, Routes, Route, useNavigate, useSearchParams } from "react-router-dom";
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
import { stripeService } from "./services/stripeService";

import type { SimulationFormData } from "./types/simulation";

const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

const HomePage: React.FC<{ onSubmit: (data: SimulationFormData) => Promise<void>; isLoading: boolean }> = ({ onSubmit, isLoading }) => (
  <motion.div key="home" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>
    <HeroSection />
    <FeaturesSection />
    <HowItWorksSection />
    <section id="simulator" className="py-20 bg-stone-100/50 border-y border-stone-200/60">
      <div className="max-w-5xl mx-auto px-5">
        <LifeChoiceForm onSubmit={onSubmit} isLoading={isLoading} />
      </div>
    </section>
    <PricingSection />
    <FooterSection />
  </motion.div>
);

const SuccessPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [verifying, setVerifying] = useState(true);

  useEffect(() => {
    const sessionId = searchParams.get("session_id");
    if (sessionId) {
      stripeService.pollPaymentStatus(sessionId).then((result) => {
        if (!result.success) {
          console.error("Payment verification failed:", result.reason || result.error);
        }
        setVerifying(false);
        navigate("/account", { replace: true });
      });
    } else {
      setVerifying(false);
      navigate("/account", { replace: true });
    }
  }, [searchParams, navigate]);

  if (verifying) {
    return (
      <div className="pt-20 pb-20 min-h-screen bg-stone-50 flex items-center justify-center">
        <p className="text-stone-500 text-sm">Verifying payment...</p>
      </div>
    );
  }

  return null;
};

const AppContent: React.FC = () => {
  const navigate = useNavigate();
  const {} = useAuth();
  const { simulation, isLoading, createSimulation, resetSimulation, setSimulation } = useSimulation();

  const handleSimulationSubmit = async (formData: SimulationFormData): Promise<void> => {
    try {
      await createSimulation(formData);
      navigate("/results");
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

  const handleNewSimulation = () => { resetSimulation(); navigate("/"); };
  const handleLogoClick = () => { resetSimulation(); navigate("/"); };
  const handleViewSimulation = (sim: import("./types/api").SimulationResult) => {
    setSimulation(sim);
    navigate("/results");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen">
      <Navigation onLogoClick={handleLogoClick} onSubscriptionClick={() => navigate("/account")} />

      <main>
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<HomePage onSubmit={handleSimulationSubmit} isLoading={isLoading} />} />

            <Route path="/results" element={
              simulation ? (
                <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}
                  className="pt-20 pb-20 min-h-screen bg-stone-50">
                  <div className="max-w-5xl mx-auto px-5">
                    <SimulationResults simulation={simulation} onNewSimulation={handleNewSimulation} />
                  </div>
                </motion.div>
              ) : (
                <motion.div key="no-results" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}
                  className="pt-20 pb-20 min-h-screen bg-stone-50 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-stone-500 text-sm mb-4">No simulation results to display.</p>
                    <button onClick={() => navigate("/")} className="text-sm text-stone-900 underline underline-offset-2 hover:text-stone-600">
                      Run a simulation
                    </button>
                  </div>
                </motion.div>
              )
            } />

            <Route path="/account" element={
              <motion.div key="subscription" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}
                className="pt-20 pb-20 min-h-screen bg-stone-50">
                <div className="max-w-5xl mx-auto px-5">
                  <SubscriptionStatus onViewSimulation={handleViewSimulation} />
                </div>
              </motion.div>
            } />

            <Route path="/success" element={<SuccessPage />} />

            <Route path="*" element={<HomePage onSubmit={handleSimulationSubmit} isLoading={isLoading} />} />
          </Routes>
        </AnimatePresence>
      </main>
    </div>
  );
};

const App: React.FC = () => {
  if (!CLERK_PUBLISHABLE_KEY) {
    return <div className="flex items-center justify-center min-h-screen"><p className="text-red-600 text-sm">Missing Clerk publishable key</p></div>;
  }
  return (
    <BrowserRouter>
      <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
        <AppContent />
      </ClerkProvider>
    </BrowserRouter>
  );
};

export default App;
