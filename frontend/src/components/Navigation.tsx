import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';
import { useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

interface NavigationProps {
  onLogoClick: () => void;
  onSubscriptionClick?: () => void;
}

const Navigation: React.FC<NavigationProps> = ({ onLogoClick, onSubscriptionClick }) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const scrollTo = (id: string) => {
    setMobileOpen(false);
    if (location.pathname !== '/') {
      onLogoClick();
      setTimeout(() => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } else {
      document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <nav className={`fixed top-0 w-full z-50 transition-colors duration-200 ${
      scrolled ? 'bg-white/90 backdrop-blur-md border-b border-stone-200' : 'bg-transparent'
    }`}>
      <div className="max-w-5xl mx-auto px-5">
        <div className="flex justify-between items-center h-14">
          <button onClick={onLogoClick} className={`font-display text-xl tracking-tight italic transition-colors ${
            scrolled ? 'text-stone-900' : 'text-white'
          }`}>
            parallax
          </button>

          <div className="hidden md:flex items-center gap-6 text-[13px]">
            {['features', 'pricing'].map((s) => (
              <button key={s} onClick={() => scrollTo(s)} className={`hover:text-stone-900 transition-colors capitalize ${
                scrolled ? 'text-stone-500' : 'text-stone-400 hover:text-white'
              }`}>
                {s}
              </button>
            ))}
            <SignedIn>
              <button onClick={onSubscriptionClick} className={`hover:text-stone-900 transition-colors ${
                scrolled ? 'text-stone-500' : 'text-stone-400 hover:text-white'
              }`}>
                Account
              </button>
            </SignedIn>
          </div>

          <div className="flex items-center gap-3">
            <SignedOut>
              <SignInButton>
                <button className={`hidden md:block text-[13px] font-medium transition-colors ${
                  scrolled ? 'text-stone-900 hover:text-stone-600' : 'text-white hover:text-stone-300'
                }`}>
                  Sign in
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <UserButton />
            </SignedIn>
            <button onClick={() => setMobileOpen(!mobileOpen)} className={`md:hidden p-1.5 ${
              scrolled ? 'text-stone-600' : 'text-white'
            }`}>
              {mobileOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-white border-b border-stone-200"
          >
            <div className="px-5 py-3 space-y-1">
              {['features', 'pricing'].map((s) => (
                <button key={s} onClick={() => scrollTo(s)} className="block w-full text-left py-2.5 text-sm text-stone-600 hover:text-stone-900 capitalize">
                  {s}
                </button>
              ))}
              <SignedIn>
                <button onClick={() => { setMobileOpen(false); onSubscriptionClick?.(); }} className="block w-full text-left py-2.5 text-sm text-stone-600">
                  Account
                </button>
              </SignedIn>
              <SignedOut>
                <SignInButton>
                  <button className="block w-full text-left py-2.5 text-sm font-medium text-stone-900">Sign in</button>
                </SignInButton>
              </SignedOut>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navigation;
