<script setup lang="ts">
import { useService } from '@/utils/di';
import { onBeforeMount } from 'vue';
import { mdiBroom, mdiDelete, mdiNull, mdiPencil, mdiPlusCircleOutline } from '@mdi/js';
import {
  VToolbar,
  VDataTableServer,
  VBtn,
  VSpacer,
  VIcon,
} from 'vuetify/components'
import { ref } from 'vue';
import PopupForm from '@/core/components/PopupForm.vue';
import { WorldApiService } from '../WorldApiService';
import type { ExtendedWorldDto, WorldDto } from '../world-dto';
import { usePageStore } from '@/core/page-store';
import ApiDrivenForm from '@/core/components/ApiDrivenForm.vue';
import { linkFactory } from '@/router';
import StatusMarker from '../components/StatusMarker.vue';

const worldApiService = useService(WorldApiService);

const createApiDriver = worldApiService.makeCreateWorldDriver()
const editApiDriver = worldApiService.makeEditWorldDriver()

const pageStore = usePageStore();

onBeforeMount(async () => {
  pageStore.setTitle('Worlds');
});

const editedItem = ref<WorldDto>();

const serverItems = ref<ExtendedWorldDto[]>([])
const loading = ref(true)
const createPopup = ref<InstanceType<typeof PopupForm>>()
const editPopup = ref<InstanceType<typeof PopupForm>>()

const createItem = async () => {
  if (await createPopup.value?.show()) {
    await loadItems()
  }
};

const editItem = async (item: WorldDto) => {
  editedItem.value = item
  if (await editPopup.value?.show()) {
    await loadItems()
  }
};

const loadItems = async () => {
  loading.value = true
  try {
    serverItems.value = await worldApiService.getWorldsExtended();
  } catch (e) {
    pageStore.notifyException(e)
  }
  loading.value = false;
}

const deleteItem = async (item: WorldDto) => {
  if (!await pageStore.confirm(`Deleting world '${item.title}'`)) {
    return
  }
  try {
    await worldApiService.deleteWorld(item)
  } catch (e) {
    pageStore.notifyException(e)
  }
  await loadItems()
};

const clearItem = async (item: WorldDto) => {
  if (!await pageStore.confirm(`Clearing world '${item.title}'`)) {
    return
  }
  try {
    await worldApiService.clearWorld(item)
  } catch (e) {
    pageStore.notifyException(e)
  }
  await loadItems()
};

const headers = [
  { key: 'id', title: '#', sortable: true },
  { key: 'title', title: 'Title', sortable: true },
  { key: 'plugin', title: 'Plugin', sortable: true },
  { key: 'initialized', title: 'Initialized', sortable: false },
  { key: 'running', title: 'Running', sortable: false },
  { key: 'actions', title: 'Actions', sortable: false },
]

</script>

<template>
  <PopupForm ref="createPopup" title="Adding" v-slot="{ submit, close }">
    <ApiDrivenForm class="ma-3" :driver="createApiDriver" title="Create World" @submitted="submit()">
      <template v-slot:extra-actions>
        <VBtn @click="close">Close</VBtn>
      </template>
    </ApiDrivenForm>
  </PopupForm>
  <PopupForm ref="editPopup" title="Editing" v-slot="{ submit, close }">
    <ApiDrivenForm class="ma-3" :driver="editApiDriver" title="Edit World" @submitted="submit()"
      :initial-data="editedItem" :path-data="editedItem">
      <template v-slot:extra-actions>
        <VBtn @click="close">Close</VBtn>
      </template>
    </ApiDrivenForm>
  </PopupForm>
  <VDataTableServer :headers="headers" :items="serverItems" :loading="loading" @update:options="loadItems"
    loading-text="Loading.." :items-length="serverItems.length" no-data-text="No data">
    <template v-slot:top>
      <VToolbar flat>
        <VSpacer />
        <VBtn color="primary" @click="createItem()" :prepend-icon="mdiPlusCircleOutline">Create</VBtn>
      </VToolbar>
    </template>
    <template v-slot:item.actions="{ item }">
      <div class="d-flex justify-center ga-2">
        <VIcon size="small" @click="editItem(item)" :icon="mdiPencil" />
        <VIcon size="small" @click="clearItem(item)" :icon="mdiBroom" />
        <VIcon size="small" @click="deleteItem(item)" :icon="mdiDelete" />
      </div>
    </template>
    <template v-slot:item.title="{ item }">
      <RouterLink :to="linkFactory.toWorld(item.id)" class="text-primary">{{ item.title }}</RouterLink>
    </template>
    <template v-slot:item.initialized="{ item }">
      <StatusMarker :value="item.initialized" />
    </template>
    <template v-slot:item.running="{ item }">
      <StatusMarker :value="item.running" />
    </template>
    <template v-slot:bottom><!-- Hide pagination --></template>
  </VDataTableServer>
</template>
