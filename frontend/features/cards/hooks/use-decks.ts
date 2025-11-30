import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { deckApi } from '../api/deck.api';
import type { TDeckCreate, TDeckListParams, TDeckUpdate } from '../types/deck.type';

export const deckKeys = {
  all: ['decks'] as const,
  lists: () => [...deckKeys.all, 'list'] as const,
  list: (params?: TDeckListParams) => [...deckKeys.lists(), params] as const,
  details: () => [...deckKeys.all, 'detail'] as const,
  detail: (id: number) => [...deckKeys.details(), id] as const,
};

export function useDecks(params?: TDeckListParams) {
  return useQuery({
    queryKey: deckKeys.list(params),
    queryFn: () => deckApi.getDecks(params),
  });
}

export function useDeck(deckId: number) {
  return useQuery({
    queryKey: deckKeys.detail(deckId),
    queryFn: () => deckApi.getDeck(deckId),
    enabled: !!deckId,
  });
}

export function useCreateDeck() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TDeckCreate) => deckApi.createDeck(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: deckKeys.lists() });
    },
  });
}

export function useUpdateDeck() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ deckId, data }: { deckId: number; data: TDeckUpdate }) =>
      deckApi.updateDeck(deckId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: deckKeys.lists() });
      queryClient.invalidateQueries({ queryKey: deckKeys.detail(variables.deckId) });
    },
  });
}

export function useDeleteDeck() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deckId: number) => deckApi.deleteDeck(deckId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: deckKeys.lists() });
    },
  });
}

