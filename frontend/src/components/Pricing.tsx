import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@clerk/clerk-react";
import { stripeService } from "../services/stripeService";
import { ApiError } from "../services/api";

const PricingSection: React.FC = () => {
  const { getToken, isSignedIn } = useAuth();
  const [popupMessage, setPopupMessage] = useState<string | null>(null);

  const handlePremium = async () => {
    try {
      const token = isSignedIn ? await getToken() : null;
      const checkout = await stripeService.createCheckoutSession("premium_monthly", token || undefined);
      if (checkout.url) window.location.href = checkout.url;
    } catch (error) {
      console.error("Checkout failed:", error);
      if (error instanceof ApiError && error.status === 400 && error.message.toLowerCase().includes("already have")) {
        setPopupMessage("already_premium");
      } else {
        setPopupMessage(error instanceof Error ? error.message : "Failed to start checkout.");
      }
    }
  };

  const scrollToSimulator = () => {
    document.getElementById("simulator")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section id="pricing" className="py-20 bg-white">
      <div className="max-w-5xl mx-auto px-5">
        <motion.p
          className="text-accent-600 text-sm tracking-[0.2em] uppercase mb-3 font-medium"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          Pricing
        </motion.p>
        <motion.h2
          className="font-display text-3xl sm:text-4xl text-stone-900 mb-14"
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          Start free. <span className="italic">Upgrade if you want more.</span>
        </motion.h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Free */}
          <motion.div
            className="bg-white rounded-2xl p-8 sm:p-10 border border-stone-200 shadow-elevated hover:shadow-card transition-shadow duration-300"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
          >
            <div className="flex items-baseline gap-1 mb-1">
              <span className="text-3xl font-bold text-stone-900 font-display">$0</span>
            </div>
            <p className="text-sm text-stone-400 mb-8">Free forever</p>

            <ul className="space-y-3 text-sm text-stone-600 mb-10">
              {["3 simulations / month", "ML predictions", "JSON export", "1-month history"].map((f, i) => (
                <li key={i} className="flex items-center gap-3">
                  <svg className="w-4 h-4 text-stone-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  {f}
                </li>
              ))}
            </ul>

            <button
              onClick={scrollToSimulator}
              className="w-full py-3.5 border border-stone-300 rounded-xl text-sm font-semibold text-stone-700 hover:border-stone-500 hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-stone-300 active:bg-stone-100 transition-colors"
            >
              Get started
            </button>
          </motion.div>

          {/* Premium */}
          <motion.div
            className="bg-stone-950 text-white rounded-2xl p-8 sm:p-10 relative overflow-hidden grain"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            
            <div className="flex items-baseline gap-1 mb-1">
              <span className="text-3xl font-bold font-display">$4.99</span>
              <span className="text-sm text-stone-500">/mo</span>
            </div>
            <p className="text-sm text-stone-500 mb-8">For serious planners</p>

            <ul className="space-y-3 text-sm text-stone-400 mb-10">
              {[
                "Unlimited simulations",
                "Risk assessment",
                "AI chatbot (Coming Soon)",
                "PDF, CSV, Excel exports",
                "Market analysis",
                "12-month history",
              ].map((f, i) => (
                <li key={i} className="flex items-center gap-3">
                  <svg className="w-4 h-4 text-accent-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  {f}
                </li>
              ))}
            </ul>

            <motion.button
              onClick={handlePremium}
              className="w-full py-3.5 bg-white text-stone-900 rounded-xl text-sm font-semibold hover:bg-stone-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-400 focus-visible:ring-offset-2 focus-visible:ring-offset-stone-950 active:bg-stone-200 transition-colors"
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
            >
              Start premium
            </motion.button>
          </motion.div>
        </div>
      </div>

      {/* Popup notification */}
      <AnimatePresence>
        {popupMessage && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setPopupMessage(null)}
          >
            <motion.div
              className="bg-white rounded-2xl shadow-elevated p-8 max-w-sm mx-4 text-center"
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.2 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="w-12 h-12 bg-accent-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-accent-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20 10 10 0 000-20z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-stone-900 mb-2 font-display">
                {popupMessage === "already_premium" ? "Already Premium" : "Checkout Error"}
              </h3>
              <p className="text-sm text-stone-500 mb-6">
                {popupMessage === "already_premium"
                  ? "You already have a premium subscription."
                  : popupMessage}
              </p>
              <button
                onClick={() => setPopupMessage(null)}
                className="w-full py-3 bg-stone-900 text-white rounded-xl text-sm font-semibold hover:bg-stone-800 transition-colors"
              >
                Got it
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
};

export default PricingSection;
