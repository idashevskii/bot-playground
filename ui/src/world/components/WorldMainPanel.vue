<script setup lang="ts">
import { usePageStore } from '@/core/page-store';
import { useService } from '@/utils/di';
import { computed, onBeforeMount, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { VBtn, VCard, VCardText, VChip, VCol, VContainer, VDivider, VImg, VList, VListItem, VProgressLinear, VRow, VSpacer, VTextarea, VToolbar } from 'vuetify/components';
import { WorldApiService } from '../WorldApiService';
import { type WorldStatusDto, type StageDto, type WorldDto, type StepDto, type WorldActionDto, type WorldActionDefDto } from '../world-dto';
import { mdiHistory, mdiPauseBox, mdiPlayBox, mdiRecord, mdiRefresh, mdiSkipNext } from '@mdi/js';
import CodeBlock from '@/core/components/CodeBlock.vue';
import PlaybackPanel from '../components/PlaybackPanel.vue';
import HotKey from '@/core/components/HotKey.vue';

const route = useRoute()
const router = useRouter()
const pageStore = usePageStore();

const worldId = Number(route.params.id)
const worldApiService = useService(WorldApiService);

const world = ref<WorldDto>()
const worldStatus = ref<WorldStatusDto>()
const worldStatusWatch = worldApiService.useWatchStatusWs(worldId)
const worldActions = ref<WorldActionDefDto[]>()
const isRunning = computed(() => Boolean(worldStatus.value && worldStatus.value.isRunning))
const initialStepId = Number(route.query.step) || undefined
const currentStepId = ref<number>()
const currentStepIsLast = ref(false) // store flag, if current step was last. Must not be computed
const lastStepId = computed(() => {
  const steps = worldStatus.value?.steps;
  if (!steps) {
    return;
  }
  return steps[steps.length - 1].id;
})
const currentStageId = computed(() => {
  const _currentStepId = currentStepId.value
  const steps = worldStatus.value?.steps;
  if (!_currentStepId || !steps) {
    return;
  }
  for (const { id, stageId } of steps) {
    if (_currentStepId === id) {
      return stageId
    }
  }
})
const numStepsPerStage = computed(() => {
  const ret: Record<number, number> = {}
  const steps = worldStatus.value?.steps;
  if (!steps) {
    return ret;
  }
  for (const { stageId } of steps) {
    if (!ret[stageId]) {
      ret[stageId] = 0
    }
    ret[stageId] += 1
  }
  return ret
})
const currentStageSteps = computed(() => {
  const ret: number[] = []
  const _currentStageId = currentStageId.value
  const steps = worldStatus.value?.steps;
  if (!_currentStageId || !steps) {
    return ret;
  }
  for (const { id, stageId } of steps) {
    if (stageId === _currentStageId) {
      ret.push(id)
    }
  }
  return ret;
})
const currentStepPos = computed(() => {
  const stageSteps = currentStageSteps.value;
  const stepId = currentStepId.value;
  return stepId ? stageSteps.indexOf(stepId) : -1
})

const stages = ref<StageDto[]>([])
const stageHtmlEls = ref<Record<number, any>>({})

const renderedStep = ref<StepDto>()
const loading = ref(false)

onBeforeMount(async () => {
  pageStore.setTitle(`...`);
  try {
    world.value = await worldApiService.getWorld(worldId)
    worldActions.value = await worldApiService.getWorldActions(worldId)
  } catch (e) {
    pageStore.notifyException(e)
  }

  await updateStatus()
  if (!currentStepId.value) {
    if (initialStepId) {
      setCurrentStep(initialStepId)
    } else if (lastStepId.value) {
      setCurrentStep(lastStepId.value)
    } else {
      setCurrentStep(undefined) // will mark step as last for live mode
    }
  }
});

const setCurrentStep = (stepId?: number) => {
  currentStepId.value = stepId
  currentStepIsLast.value = lastStepId.value === stepId
}

const withWorld = async (cb: (world: WorldDto) => Promise<void>) => {
  if (!world.value) {
    throw new Error('World is not defined')
  }
  loading.value = true
  try {
    await cb(world.value)
  } catch (e) {
    pageStore.notifyException(e)
  } finally {
    loading.value = false
  }
}

const loadStages = () => withWorld(async (world: WorldDto) => {
  stages.value = await worldApiService.getWorldStages(world.id)
  // for (const _ of range(5)) {
  //   stages.value = stages.value.concat(stages.value)
  // }
})

const updateStatus = () => withWorld(async (world: WorldDto) => {
  worldStatus.value = await worldApiService.getWorldStatus(world.id)
})

const loadStep = async (stepId: number) => {
  router.push({ ...route, query: { step: stepId } })
  try {
    renderedStep.value = await worldApiService.getStep(stepId)
  } catch (e) {
    pageStore.notifyException(e)
  }
}

const sendAction = (action: WorldActionDefDto) => withWorld(async (world: WorldDto) => {
  await worldApiService.sendAction(world.id, { name: action.name })
})

const onWorldStop = () => withWorld(async (world: WorldDto) => {
  await worldApiService.worldStop(world.id)
})
const onWorldStart = () => withWorld(async (world: WorldDto) => {
  await worldApiService.worldStart(world.id)
})
const onWorldTick = () => withWorld(async (world: WorldDto) => {
  await worldApiService.worldStart(world.id, 1)
})

const seekToLive = () => {
  if (lastStepId.value && currentStepId.value !== lastStepId.value) {
    setCurrentStep(lastStepId.value)
  }
}

const selectStageStep = (stageId: number) => {
  const steps = worldStatus.value?.steps;
  if (!steps) {
    return;
  }
  for (const { id, stageId: _stageId } of steps) {
    if (_stageId === stageId) {
      setCurrentStep(id)
      return
    }
  }
}

const getStageNumSteps = (stageId: number) => numStepsPerStage.value[stageId] || 0

const previewUrl = computed(() => {
  return currentStepId.value ? worldApiService.createStepPreviewUrl(currentStepId.value) : undefined
})

watch(currentStepId, async (val) => {
  if (val) {
    await loadStep(val)
  }
})

watch(lastStepId, async (val) => {
  // update current step only if it already was marked as last (live mode)
  if (val && currentStepIsLast.value && val != currentStepId.value) {
    currentStepId.value = val
  }
})

watch(worldStatusWatch, updateStatus)

watch(currentStageId, async (val) => {
  const missing = stages.value.every(({ id }) => id !== val)
  if (missing) {
    await loadStages()
  }
})

watch([currentStepPos, currentStageSteps], () => {
  const title = `Step ${currentStepPos.value < 0 ? '--' : currentStepPos.value + 1} of ${currentStageSteps.value.length}`
  pageStore.setTitle(title)
})

</script>

<template>
  <VToolbar density="compact">
    <VBtn :prepend-icon="mdiPauseBox" @click="onWorldStop" :disabled="!isRunning">Stop</VBtn>
    <VBtn :prepend-icon="mdiPlayBox" @click="onWorldStart" :disabled="isRunning">Start</VBtn>
    <VBtn :prepend-icon="mdiSkipNext" @click="onWorldTick" :disabled="isRunning">Tick</VBtn>
    <VDivider vertical />
    <VBtn @click="updateStatus" class="ms-2" :prepend-icon="mdiRefresh">Update</VBtn>
    <VSpacer />

    <VChip v-if="isRunning" label color="success">Running</VChip>
    <VChip v-else label>Stopped</VChip>
    <VChip v-if="currentStepIsLast" label color="info" class="ms-3" :prepend-icon="mdiRecord">Live</VChip>
    <VChip v-else label color="warning" class="ms-3" :prepend-icon="mdiHistory">Recored</VChip>
    <VBtn v-if="!currentStepIsLast" @click="seekToLive()" class="ms-2" :prepend-icon="mdiRecord">Go Live</VBtn>

    <VSpacer />
    <PlaybackPanel :frames="currentStageSteps" :current="currentStepId" @seek="setCurrentStep($event)" />
    <VProgressLinear :active="loading" indeterminate absolute bottom color="info" />
  </VToolbar>
  <VContainer fluid v-if="renderedStep">
    <VRow>
      <VCol :cols="3">
        <VRow>
          <VCol>
            <VCard title="Actions" :loading="!worldActions">
              <VList v-if="worldActions">
                <VListItem v-for="action in worldActions" :key="action.name" @click="sendAction(action)">
                  {{ action.title }}
                  <template #append>
                    <HotKey v-if="action.shortcut" :shortcut="action.shortcut" @activated="sendAction(action)" />
                  </template>
                </VListItem>
              </VList>
            </VCard>
          </VCol>
        </VRow>
        <VRow>
          <VCol>
            <VCard title="Configuration"></VCard>
          </VCol>
        </VRow>
      </VCol>
      <VCol>
        <VRow>
          <VCol :cols="2">
            <VCard title="Stages">
              <VList class="overflow-y-auto fill-height" style="max-height: 360px;">
                <VListItem :ref="inst => stageHtmlEls[stage.id] = inst" @click="selectStageStep(stage.id)"
                  v-for="stage in stages" :key="stage.id" :active="stage.id === currentStageId">{{ stage.title }}
                  <template #append>
                    <VChip>{{ getStageNumSteps(stage.id) }}</VChip>
                  </template>
                </VListItem>
              </VList>
            </VCard>
          </VCol>
          <VCol>
            <VCard>
              <VCardText v-if="previewUrl" class="d-flex align-center justify-center">
                <img :src="previewUrl" height="320" />
                <!-- <VImg :src="previewUrl" height="320px" /> -->
              </VCardText>
            </VCard>
          </VCol>
          <!-- <VCol>
            <VCard title="World Settings"></VCard>
          </VCol> -->
        </VRow>
        <VRow>
          <VCol>
            <VCard title="State">
              <VCardText>
                <CodeBlock :code="renderedStep.state" />
              </VCardText>
            </VCard>
          </VCol>
          <VCol>
            <VCard title="Recorded Interactions">
              <VCardText>
                <CodeBlock :code="renderedStep.interactions" />
              </VCardText>
            </VCard>
          </VCol>
          <VCol>
            <VCard title="Recorded Actions">
              <VCardText>
                <CodeBlock :code="renderedStep.actions" />
              </VCardText>
            </VCard>
          </VCol>
        </VRow>
        <VRow>
          <VCol>
            <VCard title="Recorded Logs">
              <VCardText>
                <CodeBlock :code="renderedStep.logs" />
              </VCardText>
            </VCard>
          </VCol>
          <VCol>
            <VCard title="Metrics">
            </VCard>
          </VCol>
        </VRow>
      </VCol>
    </VRow>
  </VContainer>
  <VContainer v-else fluid>
    <VCard>
      <VCardText>World not yet started</VCardText>
    </VCard>
  </VContainer>
</template>
