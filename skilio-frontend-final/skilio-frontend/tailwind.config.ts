import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50:'rgba(124,58,237,0.08)',100:'rgba(124,58,237,0.15)',200:'rgba(124,58,237,0.25)',
          300:'#a855f7',400:'#9333ea',500:'#7c3aed',600:'#6d28d9',700:'#5b21b6',
          800:'#4c1d95',900:'#3b0f6b',
        },
        accent: { 400:'#818cf8', 500:'#6366f1', 600:'#4f46e5' },
        gold:   { 400:'#fbbf24', 500:'#f59e0b', 600:'#d97706' },
        navy:   { 50:'#f8f7ff', 100:'#f0eeff', 800:'#140f28', 900:'#0d0a1a' },
        surface:{
          50:'#f8f7ff',100:'#f0eeff',200:'rgba(124,58,237,0.1)',300:'rgba(124,58,237,0.2)',
          400:'#c4bfe0',500:'#8b84aa',600:'#4b4470',700:'#2d2260',800:'#1a1035',900:'#0d0a1a',
        },
        ok:    { 50:'rgba(34,197,94,0.1)',   500:'#22c55e' },
        warn:  { 50:'rgba(245,158,11,0.1)',  500:'#f59e0b' },
        space: { 400:'#818cf8', 600:'#6366f1', 900:'#0d1235' },
        sea:   { 400:'#38bdf8', 600:'#0284c7', 900:'#012a4a' },
        forest:{ 400:'#4ade80', 600:'#16a34a', 900:'#071d0f' },
      },
      fontFamily: {
        display:['"Fredoka One"','cursive'],
        sans:['"Nunito"','system-ui','sans-serif'],
        mono:['"JetBrains Mono"','monospace'],
      },
      keyframes: {
        'fade-up':  {'0%':{opacity:'0',transform:'translateY(16px)'},'100%':{opacity:'1',transform:'translateY(0)'}},
        'fade-in':  {'0%':{opacity:'0'},'100%':{opacity:'1'}},
        'scale-in': {'0%':{opacity:'0',transform:'scale(0.95)'},'100%':{opacity:'1',transform:'scale(1)'}},
        'float':    {'0%,100%':{transform:'translateY(0)'},'50%':{transform:'translateY(-8px)'}},
        'twinkle':  {'0%,100%':{opacity:'0.2',transform:'scale(0.7)'},'50%':{opacity:'1',transform:'scale(1.3)'}},
        'pop-in':   {'0%':{opacity:'0',transform:'scale(0.65)'},'60%':{transform:'scale(1.08)'},'100%':{opacity:'1',transform:'scale(1)'}},
        'sway':     {'0%,100%':{transform:'rotate(-5deg)'},'50%':{transform:'rotate(5deg)'}},
      },
      animation: {
        'fade-up':  'fade-up 0.4s ease-out forwards',
        'fade-in':  'fade-in 0.3s ease-out forwards',
        'scale-in': 'scale-in 0.25s ease-out forwards',
        'float':    'float 3s ease-in-out infinite',
        'twinkle':  'twinkle 2.2s ease-in-out infinite',
        'pop-in':   'pop-in 0.45s cubic-bezier(.34,1.56,.64,1) forwards',
        'sway':     'sway 3s ease-in-out infinite',
      },
      boxShadow: {
        'card':      '0 2px 8px rgba(124,58,237,0.06)',
        'card-hover':'0 8px 24px rgba(124,58,237,0.14)',
        'glow-pu':   '0 0 20px rgba(124,58,237,0.4)',
        'glow-gold': '0 0 20px rgba(251,191,36,0.4)',
      },
    },
  },
  plugins: [],
} satisfies Config
