import { DeckPage } from '@/pages/deck.page';

export default async function Deck({ params }: PageProps<'/decks/[deckId]'>) {
  const deckId = (await params).deckId;
  return <DeckPage deckId={deckId} />;
}
