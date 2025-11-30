'use client';

import { useAppStoreApi } from '@/components/providers/zustand.provider';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Deck, useDeck } from '@/features/cards';
import Link from 'next/link';

export function DeckPage({ deckId }: { deckId: string }) {
  const deckIdNum = parseInt(deckId, 10);
  const { data: deck, isLoading, error } = useDeck(deckIdNum);
  const auth = useAppStoreApi().use.authorization();

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Skeleton className="h-8 w-64 mb-4" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (error || !deck) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <p className="text-destructive">
          Error loading deck. Please try again.
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">{deck.title}</h1>
        {deck.description && (
          <p className="text-muted-foreground mb-4">{deck.description}</p>
        )}
        <div className="flex flex-wrap gap-2 mb-4">
          <Link href={`/decks/${deckId}/learn`}>
            <Button>Learn Mode</Button>
          </Link>
          <Link href={`/decks/${deckId}/study`}>
            <Button variant="outline">Study Mode</Button>
          </Link>
          {auth && (
            <Link href={`/decks/${deckId}/edit`}>
              <Button variant="outline">Edit</Button>
            </Link>
          )}
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4">
          Cards ({deck.cards.length})
        </h2>
        <Deck cards={deck.cards} deckId={deckId} />
      </div>
    </div>
  );
}
