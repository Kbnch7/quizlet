'use client';

import { useAppStoreApi } from '@/components/providers/zustand.provider';
import { Avatar } from '@/components/ui/avatar';
import {
  NavigationMenuItem,
  NavigationMenuLink,
  navigationMenuTriggerStyle,
} from '@/components/ui/navigation-menu';
import { Skeleton } from '@/components/ui/skeleton';
import { useMounted } from '@/hooks/use-mounted';
import { AvatarFallback } from '@radix-ui/react-avatar';
import { UserCircle } from 'lucide-react';
import Link from 'next/link';

export function ProfileNavbar() {
  const { mounted } = useMounted();
  const auth = useAppStoreApi().use.authorization();
  if (!mounted) {
    return <Skeleton className="min-w-8 min-h-8 animate-pulse"></Skeleton>;
  }
  if (!auth)
    return (
      <div className="flex flex-row gap-2">
        <NavigationMenuItem>
          <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
            <Link href={'/auth/login'}>Login</Link>
          </NavigationMenuLink>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
            <Link href={'/auth/register'}>Register</Link>
          </NavigationMenuLink>
        </NavigationMenuItem>
      </div>
    );
  return (
    <NavigationMenuItem>
      <Avatar className="bg-muted size-9">
        <AvatarFallback>
          <UserCircle className="text-primary w-full h-full" />
        </AvatarFallback>
      </Avatar>
    </NavigationMenuItem>
  );
}
