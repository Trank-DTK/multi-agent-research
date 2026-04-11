// 性能监控服务
class PerformanceMonitor {
  constructor() {
    this.metrics = []
    this.isEnabled = true
  }

  // 测量页面加载时间
  measurePageLoad() {
    if (!window.performance) return

    // 使用现代的 PerformanceNavigationTiming API
    const navigationEntry = performance.getEntriesByType('navigation')[0]
    if (!navigationEntry) {
      // 现代API不可用，不向后兼容已弃用的performance.timing
      console.warn('PerformanceNavigationTiming API不可用，跳过页面加载时间测量')
      return
    }

    const loadTime = navigationEntry.loadEventEnd - navigationEntry.startTime
    const domReadyTime = navigationEntry.domContentLoadedEventEnd - navigationEntry.startTime
    const firstPaint = performance.getEntriesByType('paint')
      .find(entry => entry.name === 'first-paint')?.startTime

    this.logMetric('page_load', loadTime)
    this.logMetric('dom_ready', domReadyTime)
    if (firstPaint) this.logMetric('first_paint', firstPaint)
  }

  // 测量API响应时间
  measureAPI(url, duration, success = true) {
    this.logMetric('api_response', duration, { url, success })

    // 慢请求告警
    if (duration > 3000) {
      console.warn(`慢请求: ${url} - ${duration}ms`)
      window.notify?.(`请求 ${url} 响应较慢 (${duration}ms)`, 'warning', 5000)
    }
  }

  // 测量组件渲染时间
  measureRender(componentName, duration) {
    this.logMetric('render_time', duration, { component: componentName })

    if (duration > 100) {
      console.warn(`慢渲染: ${componentName} - ${duration}ms`)
    }
  }

  // 记录指标
  logMetric(name, value, tags = {}) {
    const metric = {
      name,
      value,
      tags,
      timestamp: Date.now()
    }

    this.metrics.push(metric)

    // 保留最近1000条
    if (this.metrics.length > 1000) {
      this.metrics.shift()
    }

    // 开发环境下打印
    if (import.meta.env.DEV) {
      console.debug(`[性能] ${name}: ${value}ms`, tags)
    }
  }

  // 获取所有指标
  getMetrics() {
    return this.metrics
  }

  // 导出指标报告
  exportReport() {
    const report = {
      timestamp: Date.now(),
      metrics: this.metrics,
      userAgent: navigator.userAgent,
      viewport: `${window.innerWidth}x${window.innerHeight}`
    }

    console.log('性能报告:', report)
    return report
  }
}

export const performanceMonitor = new PerformanceMonitor()

// 初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    performanceMonitor.measurePageLoad()
  })
} else {
  performanceMonitor.measurePageLoad()
}