import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',   //Django后端服务器
        changeOrigin: true,
        secure: false,
        ws: true,
        //日志
        configure: (proxy, options) => {
          //代理出错
          proxy.on('error', (err, req, res) => {
            console.log('Proxy error:', err);
          });
          //请求转发时出错
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log(`[PROXY] ${req.method} ${req.url} -> ${options.target}`);
          });
          //收到响应时出错
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log(`[PROXY] ${req.method} ${req.url} <- ${proxyRes.statusCode}`);
          });
        },
      },
    },
    port: 5173,
    strictPort: false,   //如果端口被占用，自动寻找下一个可用端口
  }
})
