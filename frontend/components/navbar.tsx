import { ProfileNavbar } from '@/features/auth/components/profile-navbar';
import { SearchCards } from '@/features/cards/components/search-cards';
import Logo from '@/public/logo.svg';
import { AccessibleIcon } from '@radix-ui/react-accessible-icon';
import Image from 'next/image';
import Link from 'next/link';
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from './ui/navigation-menu';

export function Navbar() {
  return (
    <NavigationMenu className="max-w-full w-full">
      <div className="w-full items-center py-3 px-2 sm:px-4">
        <NavigationMenuList className="flex flex-row justify-between w-full">
          <NavigationMenuItem className="w-fit">
            <Link className="flex items-center flex-row gap-4" href="/decks">
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
          <NavigationMenuItem className="w-48 md:w-sm lg:w-md">
            <SearchCards />
          </NavigationMenuItem>
          <ProfileNavbar />
        </NavigationMenuList>
      </div>
    </NavigationMenu>
  );
}
