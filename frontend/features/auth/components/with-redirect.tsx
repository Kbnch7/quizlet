'use client';

import { useAppStoreApi } from '@/components/providers/zustand.provider';
import { redirect, useRouter } from 'next/navigation';
import { useEffect, type PropsWithChildren } from 'react';

// Not HOC because it would cause use client
export function WithRedirect({
  to,
  children,
}: PropsWithChildren<{ to: string }>) {
  const auth = useAppStoreApi().use.authorization();
  const router = useRouter();
  useEffect(() => {
    if (auth) {
      router.push(to);
    }
  }, [auth, router, to]);
  return children;
}
