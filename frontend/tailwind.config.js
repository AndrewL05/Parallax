/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['"Instrument Serif"', 'Georgia', 'serif'],
      },
      colors: {
        accent: {
          50: '#fef9ec',
          100: '#fdf0c8',
          200: '#fbe08d',
          300: '#f8c94d',
          400: '#f5b526',
          500: '#ec9a0c',
          600: '#d17507',
          700: '#ad530a',
          800: '#8d410e',
          900: '#74360f',
        },
      },
      boxShadow: {
        'elevated': '0 1px 2px rgba(28,25,23,0.04), 0 4px 12px rgba(28,25,23,0.06)',
        'card': '0 2px 4px rgba(28,25,23,0.03), 0 8px 24px rgba(28,25,23,0.08)',
        'float': '0 4px 8px rgba(28,25,23,0.04), 0 16px 48px rgba(28,25,23,0.12)',
      },
    },
  },
  plugins: [],
};
