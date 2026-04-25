/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark editorial theme — LearnForge AI
        background: "#0A0A0F",
        surface: "#111827",
        "surface-2": "#1E2A3B",
        "surface-3": "#243447",
        accent: "#3B82F6",        // Electric blue
        "accent-hover": "#2563EB",
        "accent-dim": "#1D4ED8",
        success: "#10B981",
        warning: "#F59E0B",
        error: "#EF4444",
        "text-primary": "#F1F5F9",
        "text-secondary": "#94A3B8",
        "text-muted": "#64748B",
        border: "#1E293B",
        "border-bright": "#334155",
      },
      fontFamily: {
        mono: ['"IBM Plex Mono"', "Fira Code", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-glow": "radial-gradient(ellipse at top, #1D4ED820 0%, transparent 70%)",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "slide-in": "slideIn 0.3s ease-out",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "shimmer": "shimmer 2s infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        slideIn: {
          "0%": { transform: "translateX(-20px)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      boxShadow: {
        "glow-blue": "0 0 20px rgba(59, 130, 246, 0.15)",
        "glow-blue-lg": "0 0 40px rgba(59, 130, 246, 0.2)",
        "card": "0 4px 24px rgba(0, 0, 0, 0.4)",
      },
    },
  },
  plugins: [],
}
