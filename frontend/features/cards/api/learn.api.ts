import { apiClient } from '@/lib/api-client';
import type {
  TLearnBatchResponse,
  TLearnProgressResponse,
  TLearnSessionCreateResponse,
  TLearnSessionResponse,
  TLearnAnswer,
} from '../types/learn.type';

export const learnApi = {
  startSession: async (
    deckId: number,
  ): Promise<TLearnSessionCreateResponse> => {
    return apiClient.post<TLearnSessionCreateResponse>(
      `/learn/deck/${deckId}/sessions`,
    );
  },

  getSession: async (sessionId: number): Promise<TLearnSessionResponse> => {
    return apiClient.get<TLearnSessionResponse>(`/learn/sessions/${sessionId}`);
  },

  getNextCard: async (sessionId: number): Promise<TLearnBatchResponse> => {
    return apiClient.get<TLearnBatchResponse>(
      `/learn/sessions/${sessionId}/next`,
    );
  },

  submitAnswer: async (
    sessionId: number,
    cardId: number,
    answer: TLearnAnswer,
  ): Promise<TLearnProgressResponse> => {
    return apiClient.post<TLearnProgressResponse>(
      `/learn/sessions/${sessionId}/cards/${cardId}/answer`,
      answer,
    );
  },

  getProgress: async (
    sessionId: number,
  ): Promise<TLearnProgressResponse> => {
    return apiClient.get<TLearnProgressResponse>(
      `/learn/sessions/${sessionId}/progress`,
    );
  },

  finishSession: async (
    sessionId: number,
  ): Promise<TLearnProgressResponse> => {
    return apiClient.post<TLearnProgressResponse>(
      `/learn/sessions/${sessionId}/finish`,
    );
  },
};

