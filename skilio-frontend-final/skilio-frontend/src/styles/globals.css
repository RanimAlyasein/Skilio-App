@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --sidebar-width: 220px;
  --tabbar-height: 0px;
}

@layer base {
  *, *::before, *::after { box-sizing: border-box; }

  html {
    font-family: 'Nunito', system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    scroll-behavior: smooth;
  }

  body {
    background: #f8f7ff;
    color: #1a1035;
    line-height: 1.6;
    min-height: 100dvh;
  }

  h1, h2, h3 {
    font-family: 'Fredoka One', cursive;
    line-height: 1.2;
  }

  :focus-visible {
    outline: 2px solid #7c3aed;
    outline-offset: 2px;
    border-radius: 4px;
  }

  button { cursor: pointer; }

  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.2); border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(124,58,237,0.35); }
}

@layer components {
  /* ── Buttons ── */
  .btn {
    @apply inline-flex items-center justify-center gap-2 rounded-xl
           font-semibold font-sans text-sm px-5 py-2.5
           transition-all duration-150 select-none
           focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2;
  }

  .btn-primary {
    @apply btn text-white active:scale-[0.98]
           focus-visible:ring-primary-400;
    background: linear-gradient(135deg, #7c3aed, #6366f1);
    box-shadow: 0 4px 14px rgba(124,58,237,0.3);
  }
  .btn-primary:hover { box-shadow: 0 6px 20px rgba(124,58,237,0.45); transform: translateY(-1px); }

  .btn-outline {
    @apply btn bg-white text-surface-600 border border-surface-300
           hover:border-primary-500 hover:text-primary-500
           active:scale-[0.98] focus-visible:ring-primary-400;
  }

  .btn-ghost {
    @apply btn text-surface-500
           hover:bg-primary-50 hover:text-primary-500
           active:scale-[0.98] focus-visible:ring-primary-400;
  }

  .btn-danger {
    @apply btn bg-red-500 text-white hover:bg-red-600
           active:scale-[0.98] focus-visible:ring-red-400;
  }

  .btn-lg  { @apply px-7 py-3.5 text-base rounded-2xl; }
  .btn-sm  { @apply px-3.5 py-1.5 text-xs rounded-lg; }
  .btn:disabled { @apply opacity-50 cursor-not-allowed pointer-events-none; }

  /* ── Inputs ── */
  .input {
    @apply w-full rounded-xl border bg-white
           px-4 py-2.5 text-sm font-sans text-surface-800
           placeholder:text-surface-400
           transition-all duration-150
           focus:outline-none focus:ring-2
           disabled:bg-surface-100 disabled:cursor-not-allowed;
    border-color: rgba(124,58,237,0.2);
  }
  .input:focus {
    border-color: #7c3aed;
    --tw-ring-color: rgba(124,58,237,0.1);
  }
  .input-error { border-color: #ef4444 !important; }

  .label { @apply block text-sm font-semibold text-surface-600 mb-1.5; }
  .field-error { @apply text-xs text-red-500 mt-1.5 flex items-center gap-1; }

  /* ── Cards ── */
  .card {
    @apply bg-white rounded-2xl shadow-card;
    border: 1px solid rgba(124,58,237,0.1);
  }
  .card-hover {
    @apply card transition-all duration-200 cursor-pointer;
  }
  .card-hover:hover {
    @apply shadow-card-hover -translate-y-0.5;
    border-color: rgba(124,58,237,0.22);
  }

  /* ── Badges ── */
  .badge {
    @apply inline-flex items-center gap-1 rounded-full px-2.5 py-0.5
           text-xs font-semibold;
  }
  .badge-purple { @apply badge bg-primary-50 text-primary-500; border: 1px solid rgba(124,58,237,0.2); }
  .badge-green  { @apply badge bg-ok-50 text-green-700;  border: 1px solid rgba(34,197,94,0.2); }
  .badge-gold   { @apply badge bg-warn-50 text-gold-600; border: 1px solid rgba(245,158,11,0.2); }
  .badge-gray   { @apply badge bg-surface-100 text-surface-500; }

  /* ── Page shell ── */
  .page-container { @apply max-w-5xl mx-auto px-6 py-8 pb-24 md:pb-8; }
  .page-title     { @apply font-display text-2xl md:text-3xl text-surface-800 mb-1; }
  .page-subtitle  { @apply text-surface-400 text-sm mb-8 font-semibold; }
  .section-heading{ @apply font-display text-lg md:text-xl text-surface-700 mb-4; }

  /* ── XP bar ── */
  .xp-bar-track { @apply h-2 w-full rounded-full overflow-hidden; background: rgba(124,58,237,0.1); }
  .xp-bar-fill  { @apply h-full rounded-full; background: linear-gradient(90deg, #fbbf24, #f59e0b); }

  /* ── Progress bar ── */
  .prog-track { @apply h-2 w-full rounded-full overflow-hidden; background: rgba(124,58,237,0.1); }
  .prog-fill  { @apply h-full rounded-full; background: linear-gradient(90deg, #7c3aed, #818cf8); }

  /* ── Skeleton ── */
  .skeleton { @apply rounded-lg animate-pulse; background: rgba(124,58,237,0.08); }

  /* ── Kids world scene elements ── */
  .scene-float  { animation: float  3.5s ease-in-out infinite; }
  .scene-float2 { animation: float2 4s   ease-in-out infinite; }
  .scene-sway   { animation: sway   3s   ease-in-out infinite; transform-origin: bottom center; }
}

@layer utilities {
  .animation-delay-100 { animation-delay: 100ms; }
  .animation-delay-200 { animation-delay: 200ms; }
  .animation-delay-300 { animation-delay: 300ms; }
  .animation-delay-400 { animation-delay: 400ms; }

  .text-gradient-pu {
    background: linear-gradient(135deg, #c084fc, #818cf8, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

/* ── Mobile bottom navigation ── */
.mob-nav {
  display: none;
  position: fixed;
  bottom: 0; left: 0; right: 0;
  z-index: 500;
  background: linear-gradient(135deg, #7c3aed, #6366f1);
  border-top: 1px solid rgba(124,58,237,0.3);
  padding: 4px 0 env(safe-area-inset-bottom, 4px);
  grid-template-columns: repeat(3, 1fr);
}
.mob-btn {
  display: flex; flex-direction: column;
  align-items: center; gap: 3px;
  padding: 8px 4px;
  border: none; background: none;
  cursor: pointer; text-decoration: none;
}
.mob-ic  { font-size: 20px; line-height: 1; color: rgba(255,255,255,0.45); }
.mob-lb  { font-size: 10px; font-weight: 700; color: rgba(255,255,255,0.45); line-height: 1; }
.mob-btn.on .mob-lb,
.mob-btn.on .mob-ic { color: #c084fc; }

@media (max-width: 640px) {
  .mob-nav { display: grid; }
  main { padding-bottom: 68px !important; }
}
