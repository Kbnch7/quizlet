import { Deck } from '@/features/cards/components/deck';

export function DeckPage({ deckId }: { deckId: string }) {
  return <Deck deckId={deckId} />;
}
