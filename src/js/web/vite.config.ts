import path from "node:path"
import tailwindcss from "@tailwindcss/vite"
import { tanstackRouter } from "@tanstack/router-plugin/vite"
import react from "@vitejs/plugin-react"
import litestar from "litestar-vite-plugin"
import { defineConfig } from "vite"

export default defineConfig({
  clearScreen: false,
  base: process.env.ASSET_URL ?? (process.env.NODE_ENV === "development" ? "/" : "/static/web/"),
  publicDir: "public",
  server: {
    allowedHosts: ["host.docker.internal"],
    cors: true,
    port: Number(process.env.VITE_PORT ?? 18101),
    proxy: {
      "/api": {
        changeOrigin: true,
        target: process.env.APP_URL ?? "http://localhost:18100",
      },
    },
  },
  build: {
    outDir: path.resolve(__dirname, "../../py/app/server/static/web"),
    emptyOutDir: true,
  },
  plugins: [
    tanstackRouter({ target: "react", autoCodeSplitting: true }),
    tailwindcss(),
    react(),
    litestar({
      input: ["src/main.tsx", "src/styles.css"],
      bundleDir: path.resolve(__dirname, "../../py/app/server/static/web"),
      hotFile: path.resolve(__dirname, "../../py/app/server/static/web/hot"),
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
