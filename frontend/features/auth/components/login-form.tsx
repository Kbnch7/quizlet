'use client';

import { FormItem } from '@/components/form-item';
import { useAppStoreApi } from '@/components/providers/zustand.provider';
import { Button } from '@/components/ui/button';
import { Form, FormField } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { loginSchema, TLogin } from '../types/login.type';
import { redirect } from 'next/navigation';
import { useEffect } from 'react';
import { WithRedirect } from './with-redirect';

export function LoginForm() {
  const form = useForm<TLogin>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  });
  const authorization = useAppStoreApi().use.authorization();
  const setAuthorization = useAppStoreApi().use.setAuthorization();
  const onSubmit = (data: TLogin) => {
    console.log(data);
    // TODO FIXME wait for backend to implement login endpoint
    setAuthorization({
      accessToken: '123',
      refreshToken: '456',
    });
  };
  useEffect(() => {
    if (authorization) {
      redirect('/decks');
    }
  }, [authorization]);
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
          <Button className="mt-2 mx-auto w-1/2" type="submit">
            Login
          </Button>
        </form>
      </Form>
    </WithRedirect>
  );
}
