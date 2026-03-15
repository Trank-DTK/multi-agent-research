/// <reference types="vite/client" />

/// 声明一个模块，告诉 TypeScript 如何处理以 .vue 结尾的文件(都是VUE组件)
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
