import { EditDeckPage } from '@/pages/edit-deck.page';

export default async function EditDeck({
  params,
}: PageProps<'/decks/[deckId]/edit'>) {
  const deckId = (await params).deckId;
  return <EditDeckPage deckId={deckId} />;
}

