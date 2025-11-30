'use client';

import { AuthModal } from '@/components/auth-modal';
import { useAppStoreApi } from '@/components/providers/zustand.provider';
import { Button } from '@/components/ui/button';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
} from '@/components/ui/sidebar';
import { Skeleton } from '@/components/ui/skeleton';
import type { TDeckListParams } from '@/features/cards';
import { useCategories, useDecks } from '@/features/cards';
import { BookOpen, History, Home, Plus } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

export function DecksPage() {
  const auth = useAppStoreApi().use.authorization();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [filters, setFilters] = useState<TDeckListParams>({
    limit: 20,
  });
  const pathname = usePathname();

  const { data: decks, isLoading } = useDecks(filters);
  const { data: categories } = useCategories();

  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
          <div className="flex items-center gap-2 px-2 py-1.5">
            <SidebarTrigger />
            <span className="font-semibold">Ruzlet</span>
          </div>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Navigation</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton asChild isActive={pathname === '/decks'}>
                    <Link href="/decks">
                      <Home className="mr-2 h-4 w-4" />
                      <span>My Decks</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === '/decks/search'}
                  >
                    <Link href="/decks/search">
                      <BookOpen className="mr-2 h-4 w-4" />
                      <span>Search Decks</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                {auth && (
                  <>
                    <SidebarMenuItem>
                      <SidebarMenuButton
                        asChild
                        isActive={pathname === '/decks/create'}
                      >
                        <Link href="/decks/create">
                          <Plus className="mr-2 h-4 w-4" />
                          <span>Create Deck</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                    <SidebarMenuItem>
                      <SidebarMenuButton asChild>
                        <Link href="/decks/history">
                          <History className="mr-2 h-4 w-4" />
                          <span>History</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  </>
                )}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
      <SidebarRail />
      <SidebarInset>
        <div className="container mx-auto px-4 py-4 sm:py-8 max-w-7xl">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <h1 className="text-2xl sm:text-3xl font-bold">My Decks</h1>
            {auth ? (
              <Link href="/decks/create">
                <Button>Create Deck</Button>
              </Link>
            ) : (
              <Button onClick={() => setShowAuthModal(true)}>
                Create Deck
              </Button>
            )}
          </div>

          <AuthModal open={showAuthModal} onOpenChange={setShowAuthModal} />

          <div className="mb-4">
            <h2 className="text-lg sm:text-xl font-semibold mb-2">
              Filter by Category
            </h2>
            <div className="flex flex-wrap gap-2">
              {categories?.map((category) => (
                <Button
                  key={category.id}
                  variant={
                    filters.category === category.slug ? 'default' : 'outline'
                  }
                  onClick={() =>
                    setFilters((prev) => ({
                      ...prev,
                      category:
                        prev.category === category.slug
                          ? undefined
                          : category.slug,
                    }))
                  }
                >
                  {category.name}
                </Button>
              ))}
            </div>
          </div>

          {isLoading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <Skeleton key={i} className="h-32" />
              ))}
            </div>
          )}

          {decks && decks.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No decks found. Create your first deck to get started!
            </div>
          )}

          {decks && decks.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {decks.map((deck) => (
                <Link
                  key={deck.id}
                  href={`/decks/${deck.id}`}
                  className="block p-4 border rounded-lg hover:shadow-md transition-shadow"
                >
                  <h3 className="text-xl font-semibold mb-2">{deck.title}</h3>
                  {deck.description && (
                    <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                      {deck.description}
                    </p>
                  )}
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <span>{deck.cards_amount} cards</span>
                    {deck.categories && deck.categories.length > 0 && (
                      <>
                        <span>•</span>
                        <span>
                          {deck.categories.map((c) => c.name).join(', ')}
                        </span>
                      </>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
