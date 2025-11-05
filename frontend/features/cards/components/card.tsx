'use client';

import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';
import { TCard } from '../types/card.type';

export function Cajrd({ card }: { card: TCard }) {
  const { back, front } = card;
  const [content, setContent] = useState(front);
  const [prev, setPrev] = useState<string | null>(null);
  const [animation, setAnimation] = useState(false);
  useEffect(() => {
    setContent(front);
    setPrev(null);
  }, [card, front]);
  const onClick = () => {
    setPrev(content);
    setContent('');
    setAnimation(true);
  };
  return (
    <div
      onClick={onClick}
      onAnimationEnd={() => {
        setAnimation(false);
        setContent(prev === front ? back : front);
      }}
      className={cn(
        'flex items-center justify-center h-full w-full rounded-2xl  bg-primary',
        animation && 'animate-(--flip)'
      )}
    >
      <h3 className={cn(content === front ? 'text-3xl font-bold' : 'text-xl')}>
        {content}
      </h3>
    </div>
  );
}
