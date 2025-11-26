import { NavigationMenuLink } from '@radix-ui/react-navigation-menu';
import Link from 'next/link';
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from './ui/navigation-menu';
import { AccessibleIcon } from '@radix-ui/react-accessible-icon';
import Logo from '@/public/logo.svg';
import Image from 'next/image';
import type { TAuthorization } from '@/features/auth/types/authorization.type';
import { SearchCards } from '@/features/cards/components/search-cards';

export function Navbar({ auth }: { auth: TAuthorization | null }) {
  return (
    <NavigationMenu className="max-w-full">
      <div className="w-full items-center py-3 px-2 sm:px-4">
        <NavigationMenuList className="flex flex-row justify-between w-full">
          <NavigationMenuItem>
            {/* <NavigationMenuLink */}
            {/* asChild */}
            {/* // className={navigationMenuTriggerStyle()} */}
            {/* > */}
            <Link className="flex items-center flex-row gap-4" href="/">
              <AccessibleIcon label="">
                <Image
                  className="bg-primary rounded-xs aspect-square w-6 object-contain"
                  src={Logo}
                  alt=""
                />
              </AccessibleIcon>
              <span className="text-2xl font-bold">Ruzlet</span>
            </Link>
            {/* </NavigationMenuLink> */}
          </NavigationMenuItem>
          <NavigationMenuItem>
            <SearchCards />
          </NavigationMenuItem>
          <div className="flex flex-row gap-2">
            <NavigationMenuItem>
              <NavigationMenuLink
                asChild
                className={navigationMenuTriggerStyle()}
              >
                <Link href={'/auth/login'}>Login</Link>
              </NavigationMenuLink>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <NavigationMenuLink
                asChild
                className={navigationMenuTriggerStyle()}
              >
                <Link href={'/auth/register'}>Register</Link>
              </NavigationMenuLink>
            </NavigationMenuItem>
          </div>
        </NavigationMenuList>
      </div>
    </NavigationMenu>
  );
}
