import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#FFFFFF",
        "ink-deep": "#F8FAFC",
        card: "#F8FAFC",
        "card-raised": "#FFFFFF",
        border: "#E2E8F0",
        "border-soft": "#E2E8F0",
        paper: "#111827",
        muted: "#64748B",
        "muted-dim": "#64748B",
        brass: "#2563EB",
        "brass-dim": "#1D4ED8",
        "brass-bright": "#2563EB",
        sage: "#2563EB",
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
        card: "0 1px 0 0 rgba(17, 24, 39, 0.04) inset, 0 8px 24px -12px rgba(0,0,0,0.1)",
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