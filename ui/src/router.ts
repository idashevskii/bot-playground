import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';

export const Route = {
  // MAIN: 'MAIN',
  WORLDS: 'WORLDS',
  WORLD: 'WORLD',
};

const makeRoute = (
  name: string,
  path: string,
  component: () => Promise<unknown>,
): RouteRecordRaw => {
  return { path, name, component };
};

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: { name: Route.WORLDS } },
    // makeRoute(Route.MAIN, '/main', () => import('@/world/views/MainView.vue')),
    makeRoute(Route.WORLDS, '/worlds', () => import('@/world/views/WorldsView.vue')),
    makeRoute(Route.WORLD, '/world/:id', () => import('@/world/views/WorldView.vue')),
  ],
});

export const linkFactory = {
  toWorld: (id: number) => ({ name: Route.WORLD, params: { id: id } }),
};

export default router;
