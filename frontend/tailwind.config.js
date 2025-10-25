/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          50: '#FFFDF7',
          100: '#FFF9E6',
          200: '#FFF3CC',
          300: '#FFE999',
          400: '#FFD54F',
          500: '#D4AF37',  // Or principal
          600: '#B8960F',
          700: '#8A7109',
          800: '#5C4C06',
          900: '#2E2603',
        },
        luxury: {
          black: '#000000',
          white: '#FFFFFF',
          gray: '#F5F5F5',
          darkGray: '#333333'
        }
      },
      fontFamily: {
        'playfair': ['Playfair Display', 'serif'],
        'montserrat': ['Montserrat', 'sans-serif'],
      },
      boxShadow: {
        'gold': '0 4px 14px rgba(212, 175, 55, 0.25)',
        'gold-lg': '0 10px 40px rgba(212, 175, 55, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in',
        'slide-up': 'slideUp 0.6s ease-out',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
    },
  },
  plugins: [],
}
