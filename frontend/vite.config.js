import { defineConfig } from "vite";

export default defineConfig({
  base: "/",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: false,
    assetsDir: "assets",
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1",
    },
  },
});
