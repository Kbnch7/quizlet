import { authStore, type AuthStore } from '@/features/auth/auth.store';
import { createStore } from 'zustand';
import { immer } from 'zustand/middleware/immer';

export type AppStore = AuthStore; // Concat stores

export const createAppStore = createStore<AppStore>()(
  immer((...args) => ({
    ...authStore(...args),
  })),
);

// return store;
// }
