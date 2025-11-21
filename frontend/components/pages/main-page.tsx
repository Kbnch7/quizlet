import Link from 'next/link';
import { Button } from '../ui/button';

export function MainPage() {
  const a = 2;
  console.log(a);
  return (
    <main className="flex flex-col gap-2 h-dvh items-center justify-center">
      <h1 className="text-4xl font-bold">What&apos;s the point of this app?</h1>
      <p>
        This app is a tool for creating and studying flashcards. It&apos;s a app
        that allows you to create flashcards and study them.
      </p>
      <p>Try it out!</p>
      <Link href={'/decks/'}>
        <Button>Get Started</Button>
      </Link>
    </main>
  );
}
