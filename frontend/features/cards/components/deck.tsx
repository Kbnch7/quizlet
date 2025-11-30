'use client';

import { TextTooltip } from '@/components/tooltip';
import { Button } from '@/components/ui/button';
import { AccessibleIcon } from '@radix-ui/react-accessible-icon';
import { ArrowLeft, ArrowRight, CheckIcon } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import type { TCard } from '../types/card.type';
import { Card } from './card';

export function Deck({ cards, deckId }: { cards: TCard[]; deckId: string }) {
  const [cardId, setCardId] = useState(0);
  const [animating, setAnimating] = useState(false);
  const [direction, setDirection] = useState<'left' | 'right' | 'in' | null>(
    null,
  );
  const { push } = useRouter();

  const handleChange = (nextIndex: number) => {
    if (animating || nextIndex < 0) return;
    if (nextIndex >= cards.length) {
      push(`/decks/${deckId}/passed`);
      return;
    }
    setAnimating(true);
    setDirection(nextIndex > cardId ? 'right' : 'left');

    setTimeout(() => {
      setCardId(nextIndex);
      setDirection('in');
      setAnimating(false);
    }, 200); // CSS duration
  };

  if (cards.length === 0) {
    return (
      <div className="flex items-center justify-center h-2/3">
        <p className="text-muted-foreground">No cards in this deck</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col m-2 w-5/6 sm:w-1/2 justify-center gap-4">
      <h2 className="text-xl font-semibold text-center text-muted-foreground">
        Cards ({cardId + 1}/{cards.length})
      </h2>
      <div className="relative aspect-3/4 overflow-hidden">
        <div
          key={cardId}
          className={`absolute inset-0 transition-all duration-200 ${
            direction === 'left'
              ? 'animate-(--slide-out-left)'
              : direction === 'right'
                ? 'animate-(--slide-out-right)'
                : direction === 'in' && 'animate-(--slide-in)'
          }`}
        >
          <Card card={cards[cardId]} />
        </div>
      </div>

      <div className="flex flex-row items-center gap-2 justify-around px-4 py-2">
        <TextTooltip label="Previous card">
          <Button
            className="rounded-full w-1/2 py-6 -mt-2"
            onClick={() => handleChange(cardId - 1)}
            variant={'outline'}
            disabled={cardId === 0}
          >
            <AccessibleIcon label="">
              <ArrowLeft />
            </AccessibleIcon>
          </Button>
        </TextTooltip>

        <TextTooltip label="Next card">
          <Button
            className="rounded-full w-1/2 py-6 -mt-2"
            variant={'outline'}
            onClick={() => handleChange(cardId + 1)}
          >
            {cardId !== cards.length - 1 ? (
              <AccessibleIcon label="">
                <ArrowRight />
              </AccessibleIcon>
            ) : (
              <AccessibleIcon label="">
                <CheckIcon />
              </AccessibleIcon>
            )}
          </Button>
        </TextTooltip>
      </div>
    </div>
  );
}
