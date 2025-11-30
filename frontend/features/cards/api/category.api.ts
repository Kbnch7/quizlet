import { apiClient } from '@/lib/api-client';
import type { TCategory } from '../types/deck.type';

export const categoryApi = {
  getCategories: async (): Promise<TCategory[]> => {
    return apiClient.get<TCategory[]>('/categories/');
  },
};
