<script setup lang="ts">
import { VCard, VList, VListItem } from 'vuetify/components';
import type { WorldActionDefDto, WorldActionDto } from '../world-dto';
import { computed } from 'vue';

const props = defineProps<{
  actionDefs: WorldActionDefDto[],
  actions: WorldActionDto[],
  height?: number
}>()

const actionTitleMap = computed(() => {
  const ret: Record<string, string> = {}
  for (const def of props.actionDefs) {
    ret[def.name] = def.title
  }
  return ret
})

</script>
<template>
  <VCard title="Applied Actions" density="compact" :height="height" class="d-flex flex-column">
    <VList class="overflow-y-auto mb-3" density="compact">
      <VListItem v-for="action in props.actions">
        {{ actionTitleMap[action.name] || action.name }}
      </VListItem>
    </VList>
  </VCard>
</template>
