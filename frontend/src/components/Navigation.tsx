import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

const AccountIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="5" width="20" height="14" rx="2" />
    <line x1="2" y1="10" x2="22" y2="10" />
  </svg>
);

interface NavigationProps {
  onLogoClick: () => void;
  onSubscriptionClick?: () => void;
}

const Navigation: React.FC<NavigationProps> = ({ onLogoClick, onSubscriptionClick }) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const isHome = location.pathname === '/';
  const light = scrolled || !isHome;

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const scrollTo = (id: string) => {
    setMobileOpen(false);
    if (!isHome) {
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
      light ? 'bg-white/90 backdrop-blur-md border-b border-stone-200' : 'bg-transparent'
    }`}>
      <div className="max-w-5xl mx-auto px-5">
        <div className="flex justify-between items-center h-14">
          <button onClick={onLogoClick} className={`font-display text-xl tracking-tight italic transition-colors ${
            light ? 'text-stone-900' : 'text-white'
          }`}>
            parallax
          </button>

          <div className="hidden md:flex items-center gap-6 text-[13px]">
            {['features', 'pricing'].map((s) => (
              <button key={s} onClick={() => scrollTo(s)} className={`hover:text-stone-900 transition-colors capitalize ${
                light ? 'text-stone-500' : 'text-stone-400 hover:text-white'
              }`}>
                {s}
              </button>
            ))}
            <button onClick={() => { navigate('/demo'); window.scrollTo({ top: 0, behavior: 'smooth' }); }} className={`hover:text-stone-900 transition-colors ${
              light ? 'text-stone-500' : 'text-stone-400 hover:text-white'
            }`}>
              Demo
            </button>
          </div>

          <div className="flex items-center gap-3">
            <SignedOut>
              <SignInButton>
                <button className={`hidden md:block text-[13px] font-medium transition-colors ${
                  light ? 'text-stone-900 hover:text-stone-600' : 'text-white hover:text-stone-300'
                }`}>
                  Sign in
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <UserButton>
                <UserButton.MenuItems>
                  <UserButton.Action
                    label="Account"
                    labelIcon={<AccountIcon />}
                    onClick={() => navigate('/account')}
                  />
                </UserButton.MenuItems>
              </UserButton>
            </SignedIn>
            <button onClick={() => setMobileOpen(!mobileOpen)} className={`md:hidden p-1.5 ${
              light ? 'text-stone-600' : 'text-white'
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
              <button onClick={() => { setMobileOpen(false); navigate('/demo'); window.scrollTo({ top: 0, behavior: 'smooth' }); }} className="block w-full text-left py-2.5 text-sm text-stone-600 hover:text-stone-900">
                Demo
              </button>
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
