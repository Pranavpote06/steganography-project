/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#080b11",
          card: "#0d131f",
          cardHover: "#131b2c",
          border: "#1f293d",
          accent: "#06b6d4",
          purple: "#9333ea",
          pink: "#ec4899",
          neonGreen: "#10b981",
        }
      },
      boxShadow: {
        'glow-cyan': '0 0 20px -2px rgba(6, 182, 212, 0.4)',
        'glow-purple': '0 0 20px -2px rgba(147, 51, 234, 0.4)',
        'glow-pink': '0 0 20px -2px rgba(236, 72, 153, 0.4)',
      }
    },
  },
  plugins: [],
}
