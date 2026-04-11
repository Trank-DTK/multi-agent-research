// 加载状态组合式函数
import { ref } from 'vue'

export function useLoading(initialState = false) {
  const loading = ref(initialState)
  const error = ref(null)

  const withLoading = async (fn, context = '') => {
    loading.value = true
    error.value = null

    try {
      const result = await fn()
      return result
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    withLoading
  }
}

export function usePagination(initialPage = 1, initialPageSize = 10) {
  const page = ref(initialPage)
  const pageSize = ref(initialPageSize)
  const total = ref(0)

  const reset = () => {
    page.value = 1
    total.value = 0
  }

  const onPageChange = (newPage) => {
    page.value = newPage
  }

  const onPageSizeChange = (newSize) => {
    pageSize.value = newSize
    page.value = 1
  }

  return {
    page,
    pageSize,
    total,
    reset,
    onPageChange,
    onPageSizeChange
  }
}