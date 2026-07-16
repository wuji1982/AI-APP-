import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import path from 'path'

export default defineConfig({
  plugins: [uni()],
  resolve: {
    alias: {
      // 解决 @openim/client-sdk 依赖解析问题
      '@openim/protocol/lib/pb/sdkws/sdkws': path.resolve(__dirname, 'node_modules/@openim/protocol/lib/index.es.js'),
      '@openim/protocol': path.resolve(__dirname, 'node_modules/@openim/protocol/lib/index.es.js'),
    }
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
