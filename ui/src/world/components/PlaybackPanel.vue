<script setup lang="ts">
import { VBtn, } from 'vuetify/components';
import { mdiFastForward, mdiFastForward10, mdiFastForward30, mdiPlay, mdiRewind, mdiRewind10, mdiRewind30, mdiSkipBackward, mdiSkipForward } from '@mdi/js';
import { computed } from 'vue';

const props = defineProps<{
  current?: number,
  frames: number[]
}>()

const emit = defineEmits<{
  seek: [number],
}>()

const currentPos = computed(() => props.current ? props.frames.indexOf(props.current) : -1)

const lastPos = computed(() => props.frames.length - 1)

const seek = (frame?: number) => {
  if (frame !== undefined) {
    emit('seek', frame)
  }
}

const seekRel = (offset: number) => {
  if (currentPos.value >= 0) {
    seek(props.frames[currentPos.value + offset])
  }
}

const seekFirst = () => {
  seek(props.frames[0])
}

const seekLast = () => {
  seek(props.frames[props.frames.length - 1])
}

const canSeelFirst = computed(() => {
  return currentPos.value > 0;
})

const canSeelLast = computed(() => {
  return currentPos.value >= 0 && currentPos.value < lastPos.value;
})

const canSeek = (offset: number) => {
  return currentPos.value >= 0 && currentPos.value + offset >= 0 && currentPos.value + offset <= lastPos.value;
}

</script>

<template>
  <VBtn :icon="mdiSkipBackward" @click="seekFirst()" :disabled="!canSeelFirst"></VBtn>
  <VBtn :icon="mdiRewind30" @click="seekRel(-30)" :disabled="!canSeek(-30)"></VBtn>
  <VBtn :icon="mdiRewind10" @click="seekRel(-10)" :disabled="!canSeek(-10)"></VBtn>
  <VBtn :icon="mdiRewind" @click="seekRel(-1)" :disabled="!canSeek(-1)"></VBtn>
  <VBtn :icon="mdiPlay" disabled></VBtn>
  <VBtn :icon="mdiFastForward" @click="seekRel(1)" :disabled="!canSeek(1)"></VBtn>
  <VBtn :icon="mdiFastForward10" @click="seekRel(10)" :disabled="!canSeek(10)"></VBtn>
  <VBtn :icon="mdiFastForward30" @click="seekRel(30)" :disabled="!canSeek(30)"></VBtn>
  <VBtn :icon="mdiSkipForward" @click="seekLast()" :disabled="!canSeelLast"></VBtn>
</template>
