/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Ubuntu', 'sans-serif'], // Define a Ubuntu como fonte principal
      },
      colors: {
        genera: {
          roxo: '#2D004B',       // Roxo escuro para textos e cabeçalho
          magenta: '#E6007E',    // Magenta oficial dos botões
          magentahover: '#C5006A' // Magenta um pouco mais escuro para o hover
        }
      }
    },
  },
  plugins: [],
}