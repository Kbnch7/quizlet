import { DeckPage } from '@/pages/deck.page';

export default async function Study({ params }: PageProps<'/decks/[deckId]/study'>) {
  const deckId = (await params).deckId;
  return <DeckPage deckId={deckId} />;
}

