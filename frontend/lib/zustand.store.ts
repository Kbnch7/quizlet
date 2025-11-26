import { authStore, type AuthStore } from '@/features/auth/auth.store';
import { createStore } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export type AppStore = AuthStore; // Concat stores

export const createAppStore = createStore<AppStore>()(
  immer(
    persist(
      (...args) => ({
        ...authStore(...args),
      }),

      {
        storage: createJSONStorage(() => localStorage),
        name: 'zustand-store',
        partialize: (state): Partial<AppStore> => ({
          authorization: state.authorization,
        }),
      },
    ),
  ),
);

// return store;
// }
