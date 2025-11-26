// TODO wait for backend to implement login endpoint

import z from 'zod';

export const loginSchema = z.object({
  username: z.string().min(3).max(50),
  password: z.string().min(5).max(255),
});

export type TLogin = z.infer<typeof loginSchema>;
