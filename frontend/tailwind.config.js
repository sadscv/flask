/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '"Inter"',
          '"Source Sans Pro"',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif'
        ]
      },
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
        accent: {
          50: '#f5f8ff',
          100: '#e7efff',
          200: '#d3e1ff',
          300: '#b0c9ff',
          400: '#84a8ff',
          500: '#5c86fb',
          600: '#3763e6',
          700: '#264bc5',
          800: '#1f3d99',
          900: '#1a3478',
        },
        neutral: {
          50: '#f5f5f7',
          100: '#ebecf0',
          200: '#d7d9e0',
          300: '#c2c6d0',
          400: '#a9aebe',
          500: '#8f95a6',
          600: '#6f758c',
          700: '#585c72',
          800: '#414456',
          900: '#292c3d',
        },
      },
      boxShadow: {
        'elevated': '0 20px 45px -20px rgba(17, 24, 39, 0.45)',
        'soft': '0 10px 30px -15px rgba(15, 23, 42, 0.35)',
        'inner-glow': 'inset 0 1px 0 rgba(255, 255, 255, 0.35)'
      },
      backdropBlur: {
        xs: '2px',
      },
      backgroundImage: {
        'glass-gradient': 'linear-gradient(140deg, rgba(255,255,255,0.85) 0%, rgba(249,250,251,0.55) 45%, rgba(236,233,255,0.35) 100%)',
        'header-gradient': 'linear-gradient(120deg, rgba(15,23,42,0.92) 0%, rgba(30,64,175,0.88) 55%, rgba(109,40,217,0.85) 100%)'
      },
      borderRadius: {
        'xl': '1.25rem',
        '2xl': '1.75rem'
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'bounce-in': 'bounceIn 0.6s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
