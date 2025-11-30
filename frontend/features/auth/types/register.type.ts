import { z } from 'zod';

export const registerSchema = z.object({
  username: z.string().min(3).max(50),
  email: z.string().email(),
  password: z.string().min(5).max(255),
});

export type TRegister = z.infer<typeof registerSchema>;

