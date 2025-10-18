/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        'russo': ['Russo One', 'sans-serif'],
        'courier': ['Courier New', 'monospace'],
      },
      colors: {
        'hockey-blue': '#003366',
        'hockey-red': '#CC0000',
        'hockey-gold': '#FFD700',
        'ice-blue': '#E6F3FF',
        'rink-white': '#FFFFFF',
      },
    },
  },
  plugins: [],
}
