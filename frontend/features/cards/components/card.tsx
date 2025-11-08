'use client';

import { cn } from '@/lib/utils';
import { Reducer, useReducer } from 'react';
import { TCard } from '../types/card.type';

type State = {
  isFlipping: boolean;
  showBack: boolean;
};

type Action =
  | { type: 'FLIP' }
  | { type: 'RESET' }
  | { type: 'SET_FLIPPING'; payload: boolean };

const initialState: State = {
  isFlipping: false,
  showBack: false,
};

const cardReducer: Reducer<State, Action> = (state, action) => {
  switch (action.type) {
    case 'FLIP':
      return { ...state, showBack: !state.showBack };
    case 'RESET':
      return { ...initialState };
    case 'SET_FLIPPING':
      return { ...state, isFlipping: action.payload };
    default:
      return state;
  }
};

export function Card({ card }: { card: TCard }) {
  const { front, back } = card;
  const [state, dispatch] = useReducer(cardReducer, initialState);

  const onClick = () => {
    if (!state.isFlipping) dispatch({ type: 'FLIP' });
  };

  return (
    <div
      className="relative w-full h-full perspective-distant"
      onClick={onClick}
    >
      <div
        onTransitionStart={() =>
          dispatch({ type: 'SET_FLIPPING', payload: true })
        }
        onTransitionEnd={() =>
          dispatch({ type: 'SET_FLIPPING', payload: false })
        }
        className={cn(
          'transform-3d transition-transform duration-250 cursor-pointer select-none relative h-full w-full',
          state.showBack && 'rotate-y-180'
        )}
      >
        <div className="absolute h-full w-full backface-hidden bg-primary flex items-center justify-center rounded-2xl text-lg font-semibold">
          {front}
        </div>
        <div className="absolute h-full w-full backface-hidden bg-primary flex items-center justify-center rounded-2xl text-lg font-semibold rotate-y-180">
          {back}
        </div>
      </div>
    </div>
  );
}
