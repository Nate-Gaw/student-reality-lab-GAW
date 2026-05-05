import { defineConfig } from "vite";

export default defineConfig({
  root: "frontend",
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5055",
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: "dist",
    emptyOutDir: true
  }
});
