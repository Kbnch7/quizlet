import { useMutation, useQueryClient } from '@tanstack/react-query';
import { cardApi } from '../api/card.api';
import { deckKeys } from './use-decks';
import type { TCardBulkItem, TCardCreate, TCardUpdate } from '../types/card.type';

export function useCreateCard(deckId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TCardCreate) => cardApi.createCard(deckId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: deckKeys.detail(deckId) });
    },
  });
}

export function useUpdateCard(deckId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ cardId, data }: { cardId: number; data: TCardUpdate }) =>
      cardApi.updateCard(deckId, cardId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: deckKeys.detail(deckId) });
    },
  });
}

export function useDeleteCard(deckId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (cardId: number) => cardApi.deleteCard(deckId, cardId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: deckKeys.detail(deckId) });
    },
  });
}

export function useBulkUpdateCards(deckId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TCardBulkItem[]) => cardApi.bulkUpdateCards(deckId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: deckKeys.detail(deckId) });
    },
  });
}

