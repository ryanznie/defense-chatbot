/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        defense: {
          navy: '#003366',
          blue: '#0066cc',
          gold: '#ffd700',
          gray: '#4a5568',
        },
      },
    },
  },
  plugins: [],
}
