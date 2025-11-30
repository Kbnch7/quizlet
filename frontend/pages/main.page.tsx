import Link from 'next/link';
import { Button } from '../components/ui/button';

export function MainPage() {
  return (
    <main className="flex flex-col gap-2 items-center justify-center px-4 py-8 sm:py-16">
      <h1 className="text-2xl sm:text-4xl font-bold text-center">
        What&apos;s the point of this app?
      </h1>
      <p className="text-center max-w-2xl text-sm sm:text-base">
        This app is a tool for creating and studying flashcards. It&apos;s a app
        that allows you to create flashcards and study them.
      </p>
      <p className="text-center text-sm sm:text-base">Try it out!</p>
      <Link href={'/decks/'}>
        <Button>Get Started</Button>
      </Link>
    </main>
  );
}
