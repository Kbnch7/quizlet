'use client';

import { useMounted } from '@/hooks/use-mounted';
import { AccessibleIcon } from '@radix-ui/react-accessible-icon';
import { MoonIcon, SunIcon } from 'lucide-react';
import { useTheme } from 'next-themes';
import { TextTooltip } from './tooltip';
import { Button } from './ui/button';
import { Skeleton } from './ui/skeleton';

export function ThemeSwitchButton() {
  const { theme, setTheme } = useTheme();
  const { mounted } = useMounted();
  const onClick = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };
  if (!mounted) {
    return (
      <Skeleton className="animate-pulse min-h-10 aspect-square"></Skeleton>
    );
  }
  return (
    <TextTooltip label="Switch theme">
      <Button onClick={onClick}>
        <AccessibleIcon label="">
          {theme !== 'light' ? <SunIcon /> : <MoonIcon />}
        </AccessibleIcon>
      </Button>
    </TextTooltip>
  );
}
