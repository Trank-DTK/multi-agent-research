// 创建一个 Pinia store 来管理主题状态，包括暗黑模式和主色调设置
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDark: localStorage.getItem('theme') === 'dark' ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches &&
        !localStorage.getItem('theme')),
    primaryColor: localStorage.getItem('primaryColor') || '#42b983',
  }),

  actions: {
    toggleTheme() {
      this.isDark = !this.isDark
      localStorage.setItem('theme', this.isDark ? 'dark' : 'light')
      this.applyTheme()
    },

    setTheme(isDark) {
      this.isDark = isDark
      localStorage.setItem('theme', isDark ? 'dark' : 'light')
      this.applyTheme()
    },

    setPrimaryColor(color) {
      this.primaryColor = color
      localStorage.setItem('primaryColor', color)
      this.applyPrimaryColor()
    },

    applyTheme() {
      if (this.isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    },

    applyPrimaryColor() {
      document.documentElement.style.setProperty('--primary-color', this.primaryColor)
    },

    init() {
      this.applyTheme()
      this.applyPrimaryColor()
    }
  }
})