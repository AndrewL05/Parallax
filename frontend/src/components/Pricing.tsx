import React from "react";
import { motion } from "framer-motion";
import { useAuth } from "@clerk/clerk-react";
import { stripeService } from "../services/stripeService";

interface Plan {
  name: string;
  price: string;
  period: string;
  features: string[];
  buttonText: string;
  buttonClass: string;
  popular: boolean;
  onClick: () => void | Promise<void>;
}

const PricingSection: React.FC = () => {
  const { getToken, isSignedIn } = useAuth();

  const handlePremiumClick = async (): Promise<void> => {
    try {
      const token = isSignedIn ? await getToken() : null;
      const checkout = await stripeService.createCheckoutSession(
        "premium_monthly",
        token || undefined
      );
      if (checkout.url) {
        window.location.href = checkout.url;
      }
    } catch (error) {
      console.error("Failed to create checkout session:", error);
      alert("Failed to start checkout. Please try again.");
    }
  };

  const handleScrollToSimulator = (): void => {
    const simulatorElement = document.getElementById("simulator");
    if (simulatorElement) {
      simulatorElement.scrollIntoView({ behavior: "smooth" });
    }
  };

  const plans: Plan[] = [
    {
      name: "Free",
      price: "$0",
      period: "forever",
      features: [
        "3 life simulations per month",
        "Basic timeline visualization",
        "AI-powered insights",
        "Community support",
      ],
      buttonText: "Get Started",
      buttonClass: "bg-gray-600 hover:bg-gray-700 text-white",
      popular: false,
      onClick: handleScrollToSimulator,
    },
    {
      name: "Premium",
      price: "$4.99",
      period: "per month",
      features: [
        "Unlimited life simulations",
        "Advanced visualizations",
        "Detailed AI analysis",
        "Export & share results",
        "Priority support",
        "Early access to new features",
      ],
      buttonText: "Start Premium",
      buttonClass:
        "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white",
      popular: true,
      onClick: handlePremiumClick,
    },
  ];

  return (
    <section id="pricing" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl font-bold text-gray-800 mb-6">
            Choose Your Plan
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Start free and upgrade as your needs grow
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              className={`bg-white rounded-2xl shadow-xl p-8 relative ${
                plan.popular ? "border-4 border-purple-500 scale-105" : ""
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-800 mb-4">
                  {plan.name}
                </h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-gray-800">
                    {plan.price}
                  </span>
                  <span className="text-gray-600 ml-2">{plan.period}</span>
                </div>
              </div>

              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center">
                    <svg
                      className="w-5 h-5 text-green-500 mr-3"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="text-gray-600">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={plan.onClick}
                className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-300 hover:shadow-lg ${plan.buttonClass}`}
              >
                {plan.buttonText}
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PricingSection;