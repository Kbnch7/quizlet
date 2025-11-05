'use client';

import { TextTooltip } from '@/components/tooltip';
import { Button } from '@/components/ui/button';
import { AccessibleIcon } from '@radix-ui/react-accessible-icon';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import { useState } from 'react';
import { TCard } from '../types/card.type';
import { Card } from './card';

const cards: TCard[] = [
  {
    front: 'Card1 Front',
    back: 'Card1 Back',
  },
  {
    front: 'Card2 Front',
    back: 'Card2 Back',
  },
  {
    front: 'Card3 Front',
    back: 'Card3 Back',
  },
];

export function Cards() {
  const [cardId, setCardId] = useState(0);
  return (
    <div className="flex flex-col h-2/3 aspect-3/4 justify-center gap-4">
      <Card card={cards[cardId]} />
      <div className="flex flex-row justify-between px-4">
        <TextTooltip label="Previous card">
          <Button
            className="rounded-full aspect-square"
            onClick={() => setCardId((prev) => prev - 1)}
            disabled={!cardId}
          >
            <AccessibleIcon label="">
              <ArrowLeft />
            </AccessibleIcon>
          </Button>
        </TextTooltip>
        <TextTooltip label="Next card">
          <AccessibleIcon label="">
            <Button
              className="rounded-full aspect-square"
              disabled={cardId === cards.length - 1}
              onClick={() => setCardId((prev) => prev + 1)}
            >
              <ArrowRight />
            </Button>
          </AccessibleIcon>
        </TextTooltip>
      </div>
    </div>
  );
}
