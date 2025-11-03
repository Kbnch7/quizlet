'use client';

import { useLayoutEffect, useState } from 'react';

export function useMounted() {
  const [mounted, setMounted] = useState<boolean>(false);
  useLayoutEffect(() => {
    // TODO
    (() => setMounted(true))();
    return () => {
      setMounted(false);
    };
  }, []);
  return { mounted };
}
