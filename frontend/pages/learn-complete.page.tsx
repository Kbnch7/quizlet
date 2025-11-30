'use client';

import { Button } from '@/components/ui/button';
import { useDeck } from '@/features/cards';
import { CheckCircle } from 'lucide-react';
import Link from 'next/link';

export function LearnCompletePage({ deckId }: { deckId: string }) {
  const deckIdNum = parseInt(deckId, 10);
  const { data: deck } = useDeck(deckIdNum);

  return (
    <div className="container mx-auto px-4 py-4 sm:py-8 max-w-4xl">
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
        <CheckCircle className="w-16 h-16 text-primary mb-4" />
        <h1 className="text-2xl sm:text-3xl font-bold mb-2">Great job!</h1>
        <p className="text-muted-foreground mb-6">
          You've completed learning {deck?.title || 'this deck'}.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
          <Link href={`/decks/${deckId}`}>
            <Button>Back to Deck</Button>
          </Link>
          <Link href={`/decks/${deckId}/learn`}>
            <Button variant="outline">Learn Again</Button>
          </Link>
          <Link href="/decks">
            <Button variant="outline">Browse Decks</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
