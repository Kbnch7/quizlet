import { apiClient } from '@/lib/api-client';
import type {
  TCard,
  TCardBulkItem,
  TCardCreate,
  TCardUpdate,
} from '../types/card.type';

export type TPresignUploadRequest = {
  filename: string;
};

export type TPresignUploadResponse = {
  put_url: string;
  get_url: string;
  object_key: string;
};

export const cardApi = {
  createCard: async (
    deckId: number,
    data: TCardCreate,
  ): Promise<TCard> => {
    return apiClient.post<TCard>(`/deck/${deckId}/cards`, data);
  },

  updateCard: async (
    deckId: number,
    cardId: number,
    data: TCardUpdate,
  ): Promise<TCard> => {
    return apiClient.patch<TCard>(`/deck/${deckId}/cards/${cardId}`, data);
  },

  deleteCard: async (deckId: number, cardId: number): Promise<void> => {
    return apiClient.delete<void>(`/deck/${deckId}/cards/${cardId}`);
  },

  bulkUpdateCards: async (
    deckId: number,
    data: TCardBulkItem[],
  ): Promise<TCard[]> => {
    return apiClient.patch<TCard[]>(`/decks/${deckId}/cards`, data);
  },

  getPresignUrl: async (
    data: TPresignUploadRequest,
  ): Promise<TPresignUploadResponse> => {
    return apiClient.post<TPresignUploadResponse>('/deck/uploads/presign', data);
  },
};

