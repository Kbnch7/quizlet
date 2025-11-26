import type { TAuthorization } from './types/authorization.type';
import type { AppStore } from '@/lib/zustand.store';
import type { TImmerStore } from '@/lib/types';
import { immer } from 'zustand/middleware/immer';

type State = {
  authorization: TAuthorization | null;
};

type Actions = {
  setAuthorization: (authorization: TAuthorization | null) => void;
};

export type AuthStore = State & Actions;

const initialState: State = {
  authorization: null,
};

export const authStore: TImmerStore<AuthStore, AppStore> = immer((set) => ({
  ...initialState,
  setAuthorization: (authorization) =>
    set((state) => {
      state.authorization = authorization;
    }),
}));
