import { apiClient } from '@/lib/api-client';
import type { TTestResult, TTestResultCreate } from '../types/test-result.type';

export const testResultApi = {
  createResult: async (
    deckId: number,
    data: TTestResultCreate,
  ): Promise<TTestResult> => {
    return apiClient.post<TTestResult>(`/deck/${deckId}/results`, data);
  },

  getResults: async (
    deckId: number,
    params?: { cursor?: number; limit?: number; user_id?: number },
  ): Promise<TTestResult[]> => {
    return apiClient.get<TTestResult[]>(`/deck/${deckId}/results`, params);
  },
};

