<script setup lang="ts">
import { VChip } from 'vuetify/components';

const props = defineProps<{
  value: boolean
}>()
</script>
<template>
  <VChip :color="props.value ? 'success' : 'warning'">{{ props.value ? 'Yes' : 'No' }}</VChip>
</template>
