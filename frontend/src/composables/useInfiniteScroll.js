// 无限滚动的组合式函数，适用于列表加载更多数据的场景
import { ref, onMounted, onUnmounted } from 'vue'

export function useInfiniteScroll(loadMore, options = {}) {
  const {
    threshold = 100,
    enabled = true
  } = options

  const loading = ref(false)
  const hasMore = ref(true)
  const observer = ref(null)

  const targetRef = ref(null)

  const loadMoreItems = async () => {
    if (loading.value || !hasMore.value || !enabled) return

    loading.value = true
    try {
      const result = await loadMore()
      hasMore.value = result.hasMore !== false
    } catch (error) {
      console.error('加载更多失败:', error)
    } finally {
      loading.value = false
    }
  }

  const setupObserver = () => {
    if (!window.IntersectionObserver) return

    observer.value = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore.value && !loading.value) {
          loadMoreItems()
        }
      },
      { threshold: 0.1, rootMargin: `${threshold}px` }
    )

    if (targetRef.value) {
      observer.value.observe(targetRef.value)
    }
  }

  onMounted(() => {
    if (enabled) {
      setupObserver()
    }
  })

  onUnmounted(() => {
    if (observer.value) {
      observer.value.disconnect()
    }
  })

  return {
    targetRef,
    loading,
    hasMore,
    loadMore: loadMoreItems
  }
}