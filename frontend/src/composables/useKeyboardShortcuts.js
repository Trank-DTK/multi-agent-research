//  全局键盘快捷键组合式函数，支持多种快捷键配置
import { onMounted, onUnmounted } from 'vue'

export function useKeyboardShortcuts(shortcuts) {
  const handleKeydown = (event) => {
    const key = event.key.toLowerCase()
    const ctrl = event.ctrlKey || event.metaKey
    const alt = event.altKey
    const shift = event.shiftKey

    for (const shortcut of shortcuts) {
      let match = true

      if (shortcut.key && shortcut.key !== key) match = false
      if (shortcut.ctrl !== undefined && shortcut.ctrl !== ctrl) match = false
      if (shortcut.alt !== undefined && shortcut.alt !== alt) match = false
      if (shortcut.shift !== undefined && shortcut.shift !== shift) match = false

      if (match) {
        event.preventDefault()
        shortcut.handler(event)
        break
      }
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
  })
}