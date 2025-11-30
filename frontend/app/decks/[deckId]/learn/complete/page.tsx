import { LearnCompletePage } from '@/pages/learn-complete.page';

export default async function LearnComplete({
  params,
}: PageProps<'/decks/[deckId]/learn/complete'>) {
  const deckId = (await params).deckId;
  return <LearnCompletePage deckId={deckId} />;
}

