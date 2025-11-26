import type { StateCreator, StoreMutatorIdentifier } from 'zustand';

export type TStore<
  LocalStore,
  GlobalStore = LocalStore,
  Mps extends [StoreMutatorIdentifier, unknown][] = [],
  Mcs extends [StoreMutatorIdentifier, unknown][] = [],
> = StateCreator<GlobalStore, Mps, Mcs, LocalStore>;

export type TImmerStore<
  LocalStore,
  GlobalStore = LocalStore,
  Mps extends [StoreMutatorIdentifier, unknown][] = [],
  Mcs extends [StoreMutatorIdentifier, unknown][] = [],
> = TStore<LocalStore, GlobalStore, Mps, [['zustand/immer', never], ...Mcs]>;
