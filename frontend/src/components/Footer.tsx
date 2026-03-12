import React from "react";

const FooterSection: React.FC = () => (
  <footer className="py-8 border-t border-stone-100 bg-white">
    <div className="max-w-5xl mx-auto px-5 flex flex-col sm:flex-row justify-between items-center gap-4">
      <span className="text-sm font-medium text-stone-900 tracking-tight">parallax</span>
      <span className="text-xs text-stone-400">&copy; {new Date().getFullYear()}</span>
    </div>
  </footer>
);

export default FooterSection;
