'use client';

import { withSelectors, type WithSelectors } from '@/lib/zustand-selectors';
import { AppStore, createAppStore } from '@/lib/zustand.store';
import { createContext, useContext, useRef } from 'react';
import { useStore } from 'zustand/react';

type AppStoreApi = WithSelectors<typeof createAppStore>;

const ZustandContext = createContext<AppStoreApi | undefined>(undefined);

export function ZustandProvider({ children }: { children: React.ReactNode }) {
  const storeApiRef = useRef<AppStoreApi | null>(null);
  if (storeApiRef.current === null) {
    storeApiRef.current = withSelectors(createAppStore);
  }
  return (
    // eslint-disable-next-line react-hooks/refs
    <ZustandContext.Provider value={storeApiRef.current}>
      {children}
    </ZustandContext.Provider>
  );
}

export function useAppStore<T>(selector: (state: AppStore) => T) {
  return useStore(useAppStoreApi(), selector);
}

export function useAppStoreApi() {
  const storeApi = useContext(ZustandContext);
  if (!storeApi) {
    throw new Error('useAppStoreApi must be used within a ZustandProvider');
  }
  return storeApi;
}
