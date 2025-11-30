'use client';

import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import type { TDeckListParams } from '@/features/cards';
import { useCategories, useDecks } from '@/features/cards';
import Link from 'next/link';
import { useState } from 'react';

export function DeckSearchPage() {
  const [searchParams, setSearchParams] = useState<TDeckListParams>({
    limit: 20,
  });
  const [searchQuery, setSearchQuery] = useState('');

  const { data: decks, isLoading, error } = useDecks(searchParams);
  const { data: categories } = useCategories();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement search by title when backend supports it
    // For now, we'll filter client-side
  };

  return (
    <div className="container mx-auto px-4 py-4 sm:py-8 max-w-6xl">
      <h1 className="text-2xl sm:text-3xl font-bold mb-6">Search Decks</h1>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search decks..."
            className="flex-1 px-4 py-2 border rounded-md"
          />
          <Button type="submit">Search</Button>
        </div>
      </form>

      <div className="mb-4">
        <h2 className="text-lg sm:text-xl font-semibold mb-2">Categories</h2>
        <div className="flex flex-wrap gap-2">
          {categories?.map((category) => (
            <Button
              key={category.id}
              variant={
                searchParams.category === category.slug ? 'default' : 'outline'
              }
              onClick={() =>
                setSearchParams((prev) => ({
                  ...prev,
                  category:
                    prev.category === category.slug ? undefined : category.slug,
                }))
              }
            >
              {category.name}
            </Button>
          ))}
        </div>
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      )}

      {error && (
        <div className="text-destructive">
          Error loading decks. Please try again.
        </div>
      )}

      {decks && decks.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          No decks found. Try adjusting your search criteria.
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
                    <span>{deck.categories.map((c) => c.name).join(', ')}</span>
                  </>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
