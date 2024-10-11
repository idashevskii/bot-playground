<script setup lang="ts" generic="T, PD=never">
import { JsonForms } from '@jsonforms/vue';
import { computed, onBeforeMount, ref } from 'vue';
import { extendedVuetifyRenderers } from '@jsonforms/vue-vuetify';
import type { JsonSchema, UISchemaElement } from '@jsonforms/core';
import { dereferenceSync } from 'dereference-json-schema';
import type { ApiDriver } from '../ApiDrivenFormService';
import { VAlert, VBtn, VCard, VCardActions, VCardText, VSpacer } from 'vuetify/components';
import { usePageStore } from '../page-store';

const pageStore = usePageStore();
const props = defineProps<{
  driver: ApiDriver<T, PD>,
  initialData?: Partial<T>,
  pathData?: PD,
  uiSchema?: UISchemaElement,
  title?: string,
}>()

const driver = props.driver

const renderers = Object.freeze([
  ...extendedVuetifyRenderers,
]);

const formInitialData = computed<Partial<T>>(() => props.initialData || {})
let currentData: T | undefined;
const currentErrors = ref<any[]>([])
const commonErrors = ref<any[]>([])
const schema = ref<JsonSchema>()
const loading = ref(false)
const form = ref<InstanceType<typeof JsonForms>>()
const formIsValid = computed(() => currentErrors.value.length === 0)
const resetIdx = ref(0)

const emit = defineEmits<{
  submitted: [],
}>()

onBeforeMount(async () => {
  const schemaWithRefs = await driver.getSchema()

  schema.value = dereferenceSync(schemaWithRefs as any) as any
});

const onChange = (evt: { data: T, errors: any[] }) => {
  currentErrors.value = evt.errors;
  currentData = evt.data
}

const reset = async () => {
  if (!await pageStore.confirm(`Reset form` + (props.title ? ` '${props.title}'` : ''))) {
    return
  }
  commonErrors.value = []
  currentData = undefined;
  resetIdx.value++;
}

const submit = async () => {
  loading.value = true
  commonErrors.value = []
  try {
    if (currentData) {
      await driver.submitData(currentData, props.pathData)
      emit('submitted')
    }
  } catch (e) {
    commonErrors.value.push(String(e))
  }
  // data.value = { ...defaultData }
  loading.value = false
}
</script>

<template>
  <VCard :title="title" :loading="loading">
    <VCardText v-if="commonErrors.length">
      <VAlert v-for="error in commonErrors" color="error">{{ error }}</VAlert>
    </VCardText>
    <JsonForms :key="resetIdx" ref="form" :data="formInitialData" :schema="schema" :uischema="uiSchema"
      :renderers="renderers" @change="onChange" />
    <VCardActions>
      <VBtn @click="reset">Reset</VBtn>
      <VSpacer />
      <slot name="extra-actions" />
      <VBtn color="primary" :disabled="loading || !formIsValid" @click="submit">Submit</VBtn>
    </VCardActions>
  </VCard>
</template>

<style>
@import '@jsonforms/vue-vuetify/lib/jsonforms-vue-vuetify.css';
</style>
