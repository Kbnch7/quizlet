import { Deck } from '@/features/cards/components/deck';

export default async function DeckPage({
  params,
}: PageProps<'/decks/[deckId]'>) {
  const { deckId } = await params;
  return (
    <main className="flex h-dvh items-center justify-center">
      <Deck deckId={deckId} />
    </main>
  );
}
