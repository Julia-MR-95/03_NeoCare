// desde la librería fast-kanban
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // base: "/fast-kanban/", // for github pages
  // server: {
  //   port: 5173,
  // }
});

//  https://vite.dev/config/
//  export default defineConfig({
//  plugins: [
//     react()
//     ]
// })
