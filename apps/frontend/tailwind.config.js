/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        industrial: {
          900: "#081121",
          800: "#13203a",
          700: "#1e3152",
          600: "#2e4d79",
          500: "#3e69a0",
          400: "#5a84b9",
          300: "#8ca8d1",
        },
        alert: {
          orange: "#f16c1f",
          red: "#d42f2f",
          green: "#38b24b",
          gray: "#7d8aa0",
        },
      },
    },
  },
  plugins: [],
};
