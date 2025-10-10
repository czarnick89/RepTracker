import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import mkcert from 'vite-plugin-mkcert'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    ...(process.env.CI ? [] : [mkcert()]),
    tailwindcss()
  ],
  server: {
    https: process.env.CI ? false : true,
    host: process.env.CI ? true : undefined,
    port: process.env.CI ? 5174 : undefined,
    strictPort: process.env.CI ? true : undefined,
  },
  // Security / production build tweaks: disable sourcemaps and strip comments
  // to avoid exposing developer comments or source maps in production.
  build: {
    sourcemap: false,
    // Use terser for production minification so we can remove comments reliably
    minify: 'terser',
    terserOptions: {
      format: {
        // Do not emit any comments in the output
        comments: false,
      },
      // optional: keep class and function names if you need them for logging/debugging
      keep_classnames: false,
      keep_fnames: false,
    },
  },
})

