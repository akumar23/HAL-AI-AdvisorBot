/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'sjsu-blue': '#0055A2',
        'sjsu-gold': '#E5A823',
      },
    },
  },
  plugins: [],
}
