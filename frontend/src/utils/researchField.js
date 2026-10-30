// Native canvas field shared by the public homepage and authentication pages.
// The caller owns its lifetime; hidden, offscreen and static scenes do not animate.
export function mountResearchField(canvas) {
  if (!canvas) return () => {}
  const document = canvas.ownerDocument
  const window = document.defaultView
  const root = canvas.closest('.public-shell')
  if (!root) return () => {}
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
  const pointer = { x: 0, y: 0, currentX: 0, currentY: 0 }
  let disposed = false
  const fieldManager = {
    fields: [],
    frame: null,
    clock: 0,
    previous: 0,
    refresh() {
      if (disposed) return
      if (this.frame !== null) window.cancelAnimationFrame(this.frame)
      this.frame = null
      for (const field of this.fields) if (field.active) field.draw(this.clock)
      if (canAnimate()) {
        this.previous = 0
        this.frame = window.requestAnimationFrame(tick)
      }
    },
  }
  function canAnimate() {
    return (
      !disposed &&
      !document.hidden &&
      root.dataset.motion !== 'static' &&
      !reducedMotion.matches &&
      fieldManager.fields.some((field) => field.active)
    )
  }
  function tick(now) {
    fieldManager.frame = null
    if (!canAnimate()) return
    fieldManager.clock += fieldManager.previous ? Math.min(40, now - fieldManager.previous) : 16
    fieldManager.previous = now
    pointer.currentX += (pointer.x - pointer.currentX) * 0.035
    pointer.currentY += (pointer.y - pointer.currentY) * 0.035
    for (const field of fieldManager.fields) if (field.active) field.draw(fieldManager.clock)
    fieldManager.frame = window.requestAnimationFrame(tick)
  }
  function createField(canvas) {
    const context = canvas.getContext('2d')
    if (!context) return null
    let width = 0,
      height = 0,
      radius = 0
    let intersecting = true
    const count = window.innerWidth < 700 ? 850 : 1700
    const points = []
    const goldenAngle = Math.PI * (3 - Math.sqrt(5))
    for (let i = 0; i < count; i++) {
      const y = 1 - (i / (count - 1)) * 2
      const ringRadius = Math.sqrt(Math.max(0, 1 - y * y))
      const angle = goldenAngle * i
      points.push({
        x: Math.cos(angle) * ringRadius,
        y,
        z: Math.sin(angle) * ringRadius,
        seed: (i * 0.61803398875) % 1,
      })
    }
    const resize = () => {
      const box = canvas.getBoundingClientRect()
      width = box.width
      height = box.height
      if (!width || !height) return
      const ratio = Math.min(window.devicePixelRatio || 1, window.innerWidth < 700 ? 1.3 : 1.7)
      canvas.width = Math.round(width * ratio)
      canvas.height = Math.round(height * ratio)
      context.setTransform(ratio, 0, 0, ratio, 0, 0)
      radius = Math.min(width * 0.31, height * 0.34)
      fieldManager.refresh()
    }
    const observer = window.ResizeObserver ? new window.ResizeObserver(resize) : null
    observer?.observe(canvas)
    const visibilityObserver = window.IntersectionObserver
      ? new window.IntersectionObserver((entries) => {
          intersecting = entries[0].isIntersecting
          fieldManager.refresh()
        })
      : null
    visibilityObserver?.observe(canvas)
    function draw(time) {
      if (!width || !height) return
      context.clearRect(0, 0, width, height)
      const light = root.dataset.theme === 'light'
      const calm = root.dataset.motion === 'calm'
      const speed = calm ? 0.000012 : 0.000028
      const angle = time * speed + pointer.currentX * 0.18
      const tilt = -0.25 + pointer.currentY * 0.11
      const sin = Math.sin(angle),
        cos = Math.cos(angle)
      const sinTilt = Math.sin(tilt),
        cosTilt = Math.cos(tilt)
      const centerX = width * (canvas.id === 'auth-field' ? 0.53 : 0.55)
      const centerY = height * 0.51
      const glow = context.createRadialGradient(
        centerX,
        centerY,
        radius * 0.03,
        centerX,
        centerY,
        radius * 1.8,
      )
      glow.addColorStop(0, light ? 'rgba(44,112,192,.055)' : 'rgba(53,125,215,.14)')
      glow.addColorStop(0.5, light ? 'rgba(44,112,192,.025)' : 'rgba(32,91,170,.07)')
      glow.addColorStop(1, 'rgba(32,91,170,0)')
      context.fillStyle = glow
      context.fillRect(0, 0, width, height)
      function project(x, y, z, expansion = 1) {
        const rotatedX = x * cos - z * sin
        const rotatedZ = x * sin + z * cos
        const rotatedY = y * cosTilt - rotatedZ * sinTilt
        const depth = y * sinTilt + rotatedZ * cosTilt
        const perspective = 2.9 / (2.9 + depth * 0.45)
        return {
          x: centerX + rotatedX * radius * perspective * expansion,
          y: centerY + rotatedY * radius * perspective * expansion,
          depth,
        }
      }
      const projected = points.map((point) => ({
        ...project(point.x, point.y, point.z),
        seed: point.seed,
      }))
      // Sparse links trace the surface rather than turning the scene into a mesh wall.
      context.lineWidth = 0.55
      for (let i = 0; i < projected.length - 13; i += 5) {
        const a = projected[i],
          b = projected[i + 13]
        if (a.depth > 0.6 || Math.abs(a.depth - b.depth) > 0.28) continue
        const distance = Math.hypot(a.x - b.x, a.y - b.y)
        if (distance > radius * 0.21) continue
        context.strokeStyle = light ? 'rgba(35,101,174,.13)' : 'rgba(99,161,224,.15)'
        context.beginPath()
        context.moveTo(a.x, a.y)
        context.lineTo(b.x, b.y)
        context.stroke()
      }
      projected.sort((a, b) => b.depth - a.depth)
      for (const point of projected) {
        const depthFactor = (1 - point.depth) / 2
        const wave = 0.85 + Math.sin(time * 0.0007 + point.seed * 14) * 0.15
        const opacity = (0.13 + depthFactor * 0.72) * wave
        const size = 0.45 + depthFactor * 0.92
        context.fillStyle = light
          ? `rgba(33,105,182,${opacity * 0.78})`
          : point.seed > 0.88
            ? `rgba(176,231,244,${opacity})`
            : `rgba(91,157,237,${opacity})`
        context.beginPath()
        context.arc(point.x, point.y, size, 0, Math.PI * 2)
        context.fill()
      }
      // Two distinct orbital arcs communicate connection around the shared core.
      for (let ring = 0; ring < 2; ring++) {
        context.beginPath()
        for (let i = 0; i <= 220; i++) {
          const phase = (i / 220) * Math.PI * 2 + time * speed * (ring ? -0.5 : 0.45)
          const x = Math.cos(phase)
          const y = Math.sin(phase) * (ring ? 0.58 : -0.42)
          const z = Math.sin(phase) * (ring ? 0.78 : 0.9)
          const point = project(x, y, z, ring ? 1.24 : 1.4)
          i ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y)
        }
        context.lineWidth = 0.7
        context.strokeStyle = light ? 'rgba(39,107,184,.2)' : 'rgba(114,186,225,.27)'
        context.stroke()
        const phase = time * speed * (ring ? -1.2 : 1.5) + ring * 2.6
        const p = project(
          Math.cos(phase),
          Math.sin(phase) * (ring ? 0.58 : -0.42),
          Math.sin(phase) * (ring ? 0.78 : 0.9),
          ring ? 1.24 : 1.4,
        )
        const spark = context.createRadialGradient(p.x, p.y, 0, p.x, p.y, 12)
        spark.addColorStop(0, light ? 'rgba(53,117,202,.45)' : 'rgba(174,227,255,.8)')
        spark.addColorStop(0.2, light ? 'rgba(53,117,202,.1)' : 'rgba(117,185,255,.2)')
        spark.addColorStop(1, 'rgba(117,185,255,0)')
        context.fillStyle = spark
        context.fillRect(p.x - 12, p.y - 12, 24, 24)
      }
    }
    return {
      draw,
      resize,
      dispose() {
        observer?.disconnect()
        visibilityObserver?.disconnect()
      },
      get active() {
        return intersecting && canvas.getBoundingClientRect().width > 0
      },
    }
  }

  const field = createField(canvas)
  if (!field) return () => {}
  fieldManager.fields.push(field)
  const move = (event) => {
    if (event.pointerType === 'touch' || !canAnimate()) return
    pointer.x = event.clientX / Math.max(1, window.innerWidth) - 0.5
    pointer.y = event.clientY / Math.max(1, window.innerHeight) - 0.5
  }
  const refresh = () => fieldManager.refresh()
  const mutation = new window.MutationObserver(refresh)
  mutation.observe(root, { attributes: true, attributeFilter: ['data-theme', 'data-motion'] })
  document.addEventListener('pointermove', move, { passive: true })
  document.addEventListener('visibilitychange', refresh)
  reducedMotion.addEventListener('change', refresh)
  window.addEventListener('resize', field.resize, { passive: true })
  field.resize()
  return () => {
    disposed = true
    if (fieldManager.frame !== null) window.cancelAnimationFrame(fieldManager.frame)
    field.dispose()
    mutation.disconnect()
    document.removeEventListener('pointermove', move)
    document.removeEventListener('visibilitychange', refresh)
    reducedMotion.removeEventListener('change', refresh)
    window.removeEventListener('resize', field.resize)
  }
}
