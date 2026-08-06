import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0E1620",
        "ink-deep": "#080D13",
        card: "#16212C",
        "card-raised": "#1C2A36",
        border: "#2A3B48",
        "border-soft": "#22303C",
        paper: "#E9E3D6",
        muted: "#93A5B3",
        "muted-dim": "#5F707D",
        brass: "#C89B4A",
        "brass-dim": "#8F7038",
        "brass-bright": "#E0B563",
        sage: "#7FA37A",
        rose: "#C1666B",
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        wide2: "0.14em",
      },
      boxShadow: {
        card: "0 1px 0 0 rgba(233, 227, 214, 0.04) inset, 0 8px 24px -12px rgba(0,0,0,0.5)",
      },
      keyframes: {
        blink: { "0%, 49%": { opacity: "1" }, "50%, 100%": { opacity: "0" } },
        fadeUp: { from: { opacity: "0", transform: "translateY(6px)" }, to: { opacity: "1", transform: "translateY(0)" } },
      },
      animation: {
        blink: "blink 1s step-end infinite",
        fadeUp: "fadeUp 0.4s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
