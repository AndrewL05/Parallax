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
    <section id="pricing" className="py-24 bg-white border-t border-stone-100">
      <div className="max-w-5xl mx-auto px-5">
        <motion.p
          className="text-stone-400 text-sm tracking-widest uppercase mb-3"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          Pricing
        </motion.p>
        <motion.h2
          className="text-3xl sm:text-4xl font-bold text-stone-900 mb-16"
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          Start free. Upgrade if you want more.
        </motion.h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-px rounded-2xl overflow-hidden border-2 border-stone-200">
          {/* Free */}
          <motion.div
            className="bg-stone-50 p-8 sm:p-10"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
          >
            <div className="flex items-baseline gap-1 mb-1">
              <span className="text-3xl font-bold text-stone-900">$0</span>
            </div>
            <p className="text-sm text-stone-400 mb-8">Free forever</p>

            <ul className="space-y-3 text-sm text-stone-600 mb-10">
              {["3 simulations / month", "ML predictions", "JSON export", "1-month history"].map((f, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-stone-400 mt-0.5">—</span> {f}
                </li>
              ))}
            </ul>

            <button
              onClick={scrollToSimulator}
              className="w-full py-3 border-2 border-stone-300 rounded-xl text-sm font-medium text-stone-700 hover:border-stone-500 transition-colors"
            >
              Get started
            </button>
          </motion.div>

          {/* Premium */}
          <motion.div
            className="bg-stone-950 text-white p-8 sm:p-10"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <div className="flex items-baseline gap-1 mb-1">
              <span className="text-3xl font-bold">$4.99</span>
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
                <li key={i} className="flex items-start gap-2">
                  <span className="text-stone-600 mt-0.5">—</span> {f}
                </li>
              ))}
            </ul>

            <button
              onClick={handlePremium}
              className="w-full py-3 bg-white text-stone-900 rounded-xl text-sm font-medium hover:bg-stone-100 transition-colors"
            >
              Start premium
            </button>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default PricingSection;
