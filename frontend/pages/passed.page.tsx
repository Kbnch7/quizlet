'use client';

import { Button } from '@/components/ui/button';
import { CheckCircle2, ArrowLeft, RotateCcw } from 'lucide-react';
import Link from 'next/link';
import { useDeck } from '@/features/cards';

export function PassedPage({ deckId }: { deckId: string }) {
  const { data: deck, isLoading } = useDeck(deckId);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-accent rounded w-1/2"></div>
          <div className="h-32 bg-accent rounded"></div>
        </div>
      </div>
    );
  }

  if (!deck) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <p className="text-muted-foreground">Deck not found</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 sm:py-12 max-w-4xl">
      <div className="flex flex-col items-center text-center space-y-6">
        <div className="p-4 rounded-full bg-primary/10">
          <CheckCircle2 className="h-16 w-16 sm:h-20 sm:w-20 text-primary" />
        </div>

        <div className="space-y-2">
          <h1 className="text-3xl sm:text-4xl font-bold">
            Deck Completed!
          </h1>
          <p className="text-lg sm:text-xl text-muted-foreground">
            You&apos;ve successfully completed &quot;{deck.title}&quot;
          </p>
        </div>

        {deck.description && (
          <p className="text-muted-foreground max-w-2xl">
            {deck.description}
          </p>
        )}

        <div className="flex flex-col sm:flex-row gap-4 pt-4">
          <Link href={`/decks/${deckId}`}>
            <Button variant="outline" className="w-full sm:w-auto">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Deck
            </Button>
          </Link>
          <Link href={`/decks/${deckId}/learn`}>
            <Button className="w-full sm:w-auto">
              <RotateCcw className="mr-2 h-4 w-4" />
              Study Again
            </Button>
          </Link>
        </div>

        <div className="mt-8 p-6 rounded-lg border bg-card w-full max-w-md">
          <h2 className="text-lg font-semibold mb-4">What&apos;s next?</h2>
          <ul className="text-left space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="text-primary">•</span>
              <span>Review difficult cards to strengthen your memory</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary">•</span>
              <span>Try different learning modes for better retention</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary">•</span>
              <span>Explore other decks to continue learning</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

