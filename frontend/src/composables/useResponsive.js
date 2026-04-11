// 响应式设计的组合式函数，提供窗口尺寸和设备类型信息
import { ref, onMounted, onUnmounted } from 'vue'

const breakpoints = {
  mobile: 768,
  tablet: 1024,
  desktop: 1280
}

export function useResponsive() {
  const windowWidth = ref(window.innerWidth)
  const windowHeight = ref(window.innerHeight)

  const isMobile = ref(windowWidth.value < breakpoints.mobile)
  const isTablet = ref(windowWidth.value >= breakpoints.mobile && windowWidth.value < breakpoints.tablet)
  const isDesktop = ref(windowWidth.value >= breakpoints.desktop)

  const handleResize = () => {
    windowWidth.value = window.innerWidth
    windowHeight.value = window.innerHeight

    isMobile.value = windowWidth.value < breakpoints.mobile
    isTablet.value = windowWidth.value >= breakpoints.mobile && windowWidth.value < breakpoints.tablet
    isDesktop.value = windowWidth.value >= breakpoints.desktop
  }

  onMounted(() => {
    window.addEventListener('resize', handleResize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })

  return {
    windowWidth,
    windowHeight,
    isMobile,
    isTablet,
    isDesktop,
    breakpoints
  }
}

export default useResponsive