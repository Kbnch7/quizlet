import type { StateCreator } from 'zustand';

// TODO: StoreMutatorIdentifier should be used to identify mutators.

export type TStore<LocalStore, GlobalStore = LocalStore> = StateCreator<
  GlobalStore,
  [],
  [],
  LocalStore
>;

export type TImmerStore<LocalStore, GlobalStore = LocalStore> = StateCreator<
  GlobalStore,
  [],
  [['zustand/immer', never]],
  LocalStore
>;

// export type TStore<
//   LocalStore,
//   GlobalStore = LocalStore,
//   Mps extends [StoreMutatorIdentifier, unknown][] = [],
//   Mcs extends [StoreMutatorIdentifier, unknown][] = [],
// > = StateCreator<
//   GlobalStore,
//   [...Mps, ['zustand/persist', never]],
//   Mcs,
//   LocalStore
// >;

// export type TImmerStore<
//   LocalStore,
//   GlobalStore = LocalStore,
//   Mps extends [StoreMutatorIdentifier, unknown][] = [],
//   Mcs extends [StoreMutatorIdentifier, unknown][] = [],
// > = TStore<
//   LocalStore,
//   GlobalStore,
//   [['zustand/immer', never], ...Mps],
//   [['zustand/immer', never], ...Mcs]
// >;
