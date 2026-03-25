/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#1a1a2e',
          mid: '#16213e',
          accent: '#e94560',
          light: '#0f3460',
        },
      },
    },
  },
  plugins: [],
};
