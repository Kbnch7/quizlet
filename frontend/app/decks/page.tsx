import Link from 'next/link';

export default function DeckPage() {
  return (
    <main className="flex h-dvh items-center justify-center">
      <Link href="/decks/1">Mock Deck 1</Link>
    </main>
  );
}
