import { LearnPage } from '@/pages/learn.page';

export default async function Learn({ params }: PageProps<'/decks/[deckId]/learn'>) {
  const deckId = (await params).deckId;
  return <LearnPage deckId={deckId} />;
}

