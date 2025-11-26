import type { TUser } from './types/user.type';

export function get_me(): TUser {
  return {
    id: '1',
    username: 'mastard',
  };
}
