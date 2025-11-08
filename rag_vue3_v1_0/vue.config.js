const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {                // 必须保留代理配置
      '/api': {
        target: 'http://localhost:8000', //'http://10.0.62.60:26945',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      }
    },
    allowedHosts: [         // 添加域名白名单
      'aiservice.byd.com',
      'batteryllm',
      '.byd.com',
      '10.0.62.60' // 添加IP到白名单
    ]
  }
})