import { apiClient } from '@/lib/api-client';
import type { TAuthorization } from './types/authorization.type';
import type { TLogin } from './types/login.type';
import type { TRegister } from './types/register.type';
import type { TUser } from './types/user.type';

export const authApi = {
  login: async (data: TLogin): Promise<TAuthorization> => {
    return {
      accessToken: '123',
      refreshToken: '456',
    };
    // TODO FIXME wait backend auth api
    // return apiClient.post<TAuthorization>('/login/', data);
  },

  register: async (data: TRegister): Promise<TAuthorization> => {
    return apiClient.post<TAuthorization>('/register/', data);
  },

  logout: async (): Promise<void> => {
    return apiClient.post<void>('/logout/');
  },

  refresh: async (refreshToken: string): Promise<TAuthorization> => {
    return apiClient.post<TAuthorization>('/refresh/', {
      refresh_token: refreshToken,
    });
  },

  getMe: async (): Promise<TUser> => {
    return apiClient.get<TUser>('/users/me');
  },
};
