<script setup lang="ts">
import { RouterView } from 'vue-router';
import { computed, ref } from 'vue';
import {
  VMain,
  VList,
  VAppBar,
  VNavigationDrawer,
  VApp,
  VAppBarNavIcon,
  VToolbarTitle,
  VListItem,
  VMenu,
  VListItemTitle,
  VBtn,
  VDialog,
  VCardTitle,
  VCardText,
  VCardActions,
  VSpacer,
  VCard,
  VCheckbox,
  VDivider,
  VTooltip,
  VSnackbar,
} from 'vuetify/components';
import { mdiChevronLeft, mdiChevronRight, mdiDotsVertical, mdiGlobeModel, mdiLogout, mdiViewDashboard } from '@mdi/js';
import { usePageStore } from './core/page-store';
import { storeToRefs } from 'pinia';
import { watch } from 'vue';
import { useDisplay } from 'vuetify';
import { refPersistent } from './utils/persistent';
import { Route } from './router';

const { mobile } = useDisplay()
const pageStore = usePageStore()
const { title, confirmations, notifications } = storeToRefs(pageStore);

watch(title, (val) => {
  window.document.title = val;
});

const logout = () => {
  window.location.reload();
};

const drawerVisible = ref(true);
const drawerCollapsed = refPersistent('drawerCollapsed', false);
const drawerHideable = computed(() => mobile.value)
const drawerCollapsable = computed(() => !drawerHideable.value)

const rail = computed(() => drawerCollapsable.value && drawerCollapsed.value)

const menuStructure = [
  [
    // { title: 'Main', route: Route.MAIN, icon: mdiViewDashboard },
    { title: 'Worlds', route: Route.WORLDS, icon: mdiGlobeModel },
  ],
];

</script>

<template>
  <VApp>
    <VNavigationDrawer v-model="drawerVisible" class="bg-indigo-darken-4" theme="dark" :rail="rail">
      <VList>
        <VListItem prepend-avatar="https://randomuser.me/api/portraits/thumb/men/14.jpg" subtitle="myuser@gmail.com"
          title="My Name" />
      </VList>
      <template v-for="items in menuStructure">
        <VDivider />
        <VList>
          <template v-if="rail">
            <VTooltip v-for="{ icon, route, title } in items" :text="title" theme="light">
              <template v-slot:activator="{ props }">
                <VListItem v-bind="props" :prepend-icon="icon" :to="{ name: route }" :title="title" />
              </template>
            </VTooltip>
          </template>
          <template v-else>
            <VListItem v-for="{ icon, route, title } in items" :prepend-icon="icon" :to="{ name: route }"
              :title="title" />
          </template>
        </VList>
      </template>

      <template v-slot:append v-if="drawerCollapsable">
        <VDivider />
        <VList>
          <VTooltip text="Expand" v-if="rail" theme="light">
            <template v-slot:activator="{ props }">
              <VListItem v-bind="props" :prepend-icon="mdiChevronRight" @click="drawerCollapsed = false" />
            </template>
          </VTooltip>
          <VListItem v-else :prepend-icon="mdiChevronLeft" @click="drawerCollapsed = true">
            Collapse
          </VListItem>
        </VList>
      </template>
    </VNavigationDrawer>

    <VAppBar density="compact" class="bg-indigo-darken-4" theme="dark" scroll-behavior="elevate">
      <template v-slot:prepend v-if="drawerHideable">
        <VAppBarNavIcon @click="drawerVisible = !drawerVisible"></VAppBarNavIcon>
      </template>

      <VToolbarTitle>{{ title }}</VToolbarTitle>

      <template v-slot:append>
        <VMenu>
          <template v-slot:activator="{ props }">
            <VBtn :icon="mdiDotsVertical" v-bind="props"></VBtn>
          </template>
          <VList>
            <VListItem @click="logout" :prepend-icon="mdiLogout">
              <VListItemTitle>Logout</VListItemTitle>
            </VListItem>
          </VList>
        </VMenu>
      </template>
    </VAppBar>

    <VMain>
      <RouterView />
    </VMain>

    <template v-for="item in confirmations" :key="item.id">
      <VDialog :model-value="true" max-width="480px" persistent>
        <VCard>
          <VCardTitle>
            <span class="text-h5">Please confirm this action</span>
          </VCardTitle>
          <VCardText>
            {{ item.question }}
          </VCardText>
          <VCardActions>
            <VCheckbox v-model="item.autoConfirm" label="Auto confirmation for a while" hide-details />
            <VSpacer></VSpacer>
            <VBtn variant="text" @click="pageStore.setConfirmed(item, false)">No</VBtn>
            <VBtn color="blue-darken-1" variant="text" @click="pageStore.setConfirmed(item, true)">Yes</VBtn>
          </VCardActions>
        </VCard>
      </VDialog>
    </template>

    <template v-for="notification in notifications" :key="notification.id">
      <VSnackbar :model-value="true" :color="notification.color">
        {{ notification.message }}
        <template v-slot:actions>
          <VBtn variant="text" @click="pageStore.markNotificationViewed(notification)">Close</VBtn>
        </template>
      </VSnackbar>
    </template>
  </VApp>
</template>
