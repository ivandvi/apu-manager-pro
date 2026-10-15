/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./nuevoindex.html",
    "./tutorials/**/*.{html,js}"
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries'),
  ],
}
