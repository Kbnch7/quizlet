import { useForm } from 'react-hook-form';
import { loginSchema, TLogin } from '../types/login.type';
import { zodResolver } from '@hookform/resolvers/zod';
import { Form } from '@/components/ui/form';
import { useAppStoreApi } from '@/components/providers/zustand.provider';

export function LoginForm() {
  const form = useForm<TLogin>({
    resolver: zodResolver(loginSchema),
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
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}></form>
    </Form>
  );
}
