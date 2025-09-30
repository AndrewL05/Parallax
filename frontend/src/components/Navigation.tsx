import React from 'react';
import { motion } from 'framer-motion';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';

interface NavigationProps {
  onLogoClick: () => void;
  onSubscriptionClick?: () => void;
}

const Navigation: React.FC<NavigationProps> = ({ onLogoClick, onSubscriptionClick }) => {
  const scrollToSection = (sectionId: string) => {
    // First go to home page if not already there
    if (onLogoClick) {
      onLogoClick();
    }

    // Then scroll to section after a small delay to allow page transition
    setTimeout(() => {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
          inline: 'nearest'
        });
      }
    }, 100);
  };

  return (
    <nav className="fixed top-0 w-full bg-white/95 backdrop-blur-md shadow-lg z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <motion.div
            className="flex items-center cursor-pointer"
            onClick={onLogoClick}
            whileHover={{ scale: 1.05 }}
          >
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Parallax
            </h1>
          </motion.div>

          <div className="hidden md:flex items-center space-x-8">
            <button
              onClick={() => scrollToSection('features')}
              className="text-gray-700 hover:text-purple-600 font-medium transition-colors"
            >
              Features
            </button>
            <button
              onClick={() => scrollToSection('how-it-works')}
              className="text-gray-700 hover:text-purple-600 font-medium transition-colors"
            >
              How It Works
            </button>
            <button
              onClick={() => scrollToSection('pricing')}
              className="text-gray-700 hover:text-purple-600 font-medium transition-colors"
            >
              Pricing
            </button>
            <SignedIn>
              <button
                onClick={onSubscriptionClick}
                className="text-gray-700 hover:text-purple-600 font-medium transition-colors"
              >
                My Subscription
              </button>
            </SignedIn>
          </div>

          <div className="flex items-center space-x-4">
            <SignedOut>
              <SignInButton>
                <motion.button
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-300"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Sign In
                </motion.button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <UserButton />
            </SignedIn>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;