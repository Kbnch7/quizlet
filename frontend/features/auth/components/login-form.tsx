'use client';

import { FormItem } from '@/components/form-item';
import { useAppStoreApi } from '@/components/providers/zustand.provider';
import { Button } from '@/components/ui/button';
import { Form, FormField } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { authApi } from '../index';
import { loginSchema, TLogin } from '../types/login.type';
import { WithRedirect } from './with-redirect';

export function LoginForm() {
  const form = useForm<TLogin>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  });
  const router = useRouter();
  const setAuthorization = useAppStoreApi().use.setAuthorization();
  const [error, setError] = useState<string | null>(null);

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      setAuthorization(data);
      router.push('/decks');
    },
    onError: (err: Error) => {
      setError(err.message || 'Login failed. Please try again.');
    },
  });

  const onSubmit = (data: TLogin) => {
    setError(null);
    loginMutation.mutate(data);
  };

  return (
    <WithRedirect to="/decks">
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-4"
        >
          <FormField
            control={form.control}
            render={({ field }) => (
              <FormItem label="Username">
                <Input placeholder="Enter your username" {...field} />
              </FormItem>
            )}
            name="username"
          />
          <FormField
            control={form.control}
            render={({ field }) => (
              <FormItem label="Password">
                <Input placeholder="Enter your password" {...field} />
              </FormItem>
            )}
            name="password"
          />
          {error && (
            <div className="text-destructive text-sm text-center">{error}</div>
          )}
          <Button
            className="mt-2 mx-auto w-1/2"
            type="submit"
            disabled={loginMutation.isPending}
          >
            {loginMutation.isPending ? 'Logging in...' : 'Login'}
          </Button>
        </form>
      </Form>
    </WithRedirect>
  );
}
