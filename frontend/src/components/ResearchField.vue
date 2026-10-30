<template>
  <canvas ref="canvas" :id="kind === 'auth' ? 'auth-field' : 'hero-field'" aria-hidden="true" />
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { mountResearchField } from '@/utils/researchField'
defineProps({ kind: { type: String, default: 'hero' } })
const canvas = ref(null)
let dispose
onMounted(() => {
  dispose = mountResearchField(canvas.value)
})
onBeforeUnmount(() => dispose?.())
</script>
