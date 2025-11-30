'use client';

import { ProfileNavbar } from '@/features/auth';
import { SearchCards } from '@/features/cards';
import { useIsMobile } from '@/hooks/use-mobile';
import Logo from '@/public/logo.svg';
import { AccessibleIcon } from '@radix-ui/react-accessible-icon';
import { Menu } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from './ui/navigation-menu';
import { SidebarTrigger } from './ui/sidebar';

function MobileNavMenu() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-56">
        <DropdownMenuItem asChild>
          <Link href="/decks" className="flex items-center gap-2">
            <span>Home</span>
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href="/decks/search" className="flex items-center gap-2">
            <span>Search Decks</span>
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/decks/create" className="flex items-center gap-2">
            <span>Create Deck</span>
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function DesktopSidebarTrigger() {
  const isMobile = useIsMobile();
  const pathname = usePathname();

  if (isMobile) return null;

  // Only render SidebarTrigger on pages that have SidebarProvider
  // Currently only /decks page has SidebarProvider
  const hasSidebar =
    pathname?.startsWith('/decks') && pathname !== '/decks/search';

  if (!hasSidebar) return null;

  return (
    <div className="hidden md:block">
      <SidebarTrigger className="size-7" />
    </div>
  );
}

export function Navbar() {
  return (
    <NavigationMenu className="max-w-full w-full">
      <div className="w-full py-3 px-2 sm:px-4">
        <NavigationMenuList className="flex flex-col gap-2 w-full">
          <div className="flex flex-row items-center justify-between w-full gap-2">
            <div className="flex items-center gap-2">
              <MobileNavMenu />
              <DesktopSidebarTrigger />
              <NavigationMenuItem className="w-fit">
                <Link
                  className="flex items-center flex-row gap-4"
                  href="/decks"
                >
                  <AccessibleIcon label="">
                    <Image
                      className="bg-primary rounded-xs aspect-square w-6 object-contain"
                      src={Logo}
                      alt=""
                    />
                  </AccessibleIcon>
                  <span className="text-2xl font-bold">Ruzlet</span>
                </Link>
              </NavigationMenuItem>
            </div>
            <NavigationMenuItem className="w-full hidden sm:block sm:w-48 md:w-sm lg:w-md">
              <SearchCards />
            </NavigationMenuItem>
            <ProfileNavbar />
          </div>
          <NavigationMenuItem className="sm:hidden w-full px-8">
            <SearchCards />
          </NavigationMenuItem>
        </NavigationMenuList>
      </div>
    </NavigationMenu>
  );
}
