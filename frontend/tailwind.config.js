/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // CivicQ brand colors (to be customized)
        'civic-blue': '#1E40AF',
        'civic-green': '#059669',
        'civic-gray': '#6B7280',
      },
      fontFamily: {
        // Clean, accessible fonts
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
