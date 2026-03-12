import React from "react";
import { motion } from "framer-motion";
import { useAuth } from "@clerk/clerk-react";
import { stripeService } from "../services/stripeService";

const PricingSection: React.FC = () => {
  const { getToken, isSignedIn } = useAuth();

  const handlePremium = async () => {
    try {
      const token = isSignedIn ? await getToken() : null;
      const checkout = await stripeService.createCheckoutSession("premium_monthly", token || undefined);
      if (checkout.url) window.location.href = checkout.url;
    } catch (error) {
      console.error("Checkout failed:", error);
      alert("Failed to start checkout.");
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
            {/* Accent border top */}
            <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-accent-400 via-accent-500 to-accent-600" />

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
    </section>
  );
};

export default PricingSection;
