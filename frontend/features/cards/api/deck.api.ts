import { apiClient } from '@/lib/api-client';
import type {
  TDeck,
  TDeckCreate,
  TDeckDetailed,
  TDeckListParams,
  TDeckUpdate,
} from '../types/deck.type';

export const deckApi = {
  getDecks: async (params?: TDeckListParams): Promise<TDeck[]> => {
    return apiClient.get<TDeck[]>('/deck/', params);
  },

  getDeck: async (deckId: number): Promise<TDeckDetailed> => {
    return apiClient.get<TDeckDetailed>(`/deck/${deckId}/`);
  },

  createDeck: async (data: TDeckCreate): Promise<TDeck> => {
    return apiClient.post<TDeck>('/deck/', data);
  },

  updateDeck: async (deckId: number, data: TDeckUpdate): Promise<TDeck> => {
    return apiClient.patch<TDeck>(`/deck/${deckId}/`, data);
  },

  deleteDeck: async (deckId: number): Promise<void> => {
    return apiClient.delete<void>(`/deck/${deckId}/`);
  },

  getDeckStats: async (deckId: number): Promise<unknown> => {
    return apiClient.get<unknown>(`/deck/${deckId}/stats/`);
  },
};
