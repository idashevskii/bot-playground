<script setup lang="ts">
import { VAlert, VCard, VCardText, VList, VListItem } from 'vuetify/components';
import type { WorldLogEntry } from '../models';

const props = defineProps<{
  logs: WorldLogEntry[],
  height?: number
}>()

const colorMap: Record<string, string> = {
  'DEBUG': 'secondary',
  'INFO': 'info',
  'WARNING': 'warning',
  'ERROR': 'error',
  'CRITICAL': 'error',
}

</script>
<template>
  <VCard title="Logs" density="compact" :height="height" class="d-flex flex-column">
    <VCardText class="overflow-y-auto mb-3">
      <VAlert v-for="log in props.logs" :color="colorMap[log.level]" class="mb-2" variant="outlined" density="compact">
        <strong>{{ log.level }}</strong>:
        {{ log.message }}
      </VAlert>
    </VCardText>
  </VCard>
</template>
