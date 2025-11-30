import { PassedPage } from '@/pages/passed.page';

export default async function Passed({
  params,
}: PageProps<'/decks/[deckId]/passed'>) {
  const deckId = (await params).deckId;
  return <PassedPage deckId={deckId} />;
}
