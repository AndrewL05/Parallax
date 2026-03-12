import React from "react";

const FooterSection: React.FC = () => (
  <footer className="py-10 border-t border-stone-200 bg-stone-50">
    <div className="max-w-5xl mx-auto px-5 flex flex-col sm:flex-row justify-between items-center gap-4">
      <span className="font-display text-lg italic text-stone-900 tracking-tight">parallax</span>
      <div className="flex items-center gap-6 text-xs text-stone-400">
        <span>&copy; {new Date().getFullYear()} Parallax</span>
      </div>
    </div>
  </footer>
);

export default FooterSection;
