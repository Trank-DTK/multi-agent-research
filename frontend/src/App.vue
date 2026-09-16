<template>
  <div :class="{ 'workspace-shell': $route.meta.requiresAuth }">
    <ResponsiveNav v-if="$route.meta.requiresAuth" />
    <div class="route-content"><router-view /></div>
    <GlobalNotification />
  </div>
</template>
<script setup>
import ResponsiveNav from './components/ResponsiveNav.vue'
import GlobalNotification from './components/GlobalNotification.vue'
</script>
