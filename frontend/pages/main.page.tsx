'use client';

import { BookOpen, TrendingUp, Zap } from 'lucide-react';
import Link from 'next/link';
import { Button } from '../components/ui/button';

export function MainPage() {
  return (
    <main className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] px-4 py-12 sm:py-20">
      {/* Hero Section */}
      <div className="flex flex-col items-center text-center max-w-4xl mx-auto mb-16 sm:mb-24">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6 bg-linear-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Master Any Subject with Flashcards
        </h1>
        <p className="text-lg sm:text-xl text-muted-foreground mb-4 max-w-2xl">
          Create, study, and master flashcards with our intuitive platform.
          Perfect for students, teachers, and lifelong learners.
        </p>
        <p className="text-base sm:text-lg text-muted-foreground mb-8 max-w-xl">
          Join thousands of learners who are already improving their memory and
          knowledge retention.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <Link href="/decks">
            <Button size="lg" className="w-full sm:w-auto">
              Get Started
            </Button>
          </Link>
          <Link href="/decks/search">
            <Button size="lg" variant="outline" className="w-full sm:w-auto">
              Browse Decks
            </Button>
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto w-full mb-16">
        <div className="flex flex-col items-center text-center p-6 rounded-lg border bg-card">
          <div className="p-3 rounded-full bg-primary/10 mb-4">
            <Zap className="h-6 w-6 text-primary" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Fast Learning</h3>
          <p className="text-muted-foreground text-sm">
            Study efficiently with spaced repetition and interactive learning
            modes.
          </p>
        </div>

        <div className="flex flex-col items-center text-center p-6 rounded-lg border bg-card">
          <div className="p-3 rounded-full bg-primary/10 mb-4">
            <BookOpen className="h-6 w-6 text-primary" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Create & Share</h3>
          <p className="text-muted-foreground text-sm">
            Build your own flashcard decks or explore thousands created by the
            community.
          </p>
        </div>

        <div className="flex flex-col items-center text-center p-6 rounded-lg border bg-card">
          <div className="p-3 rounded-full bg-primary/10 mb-4">
            <TrendingUp className="h-6 w-6 text-primary" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Track Progress</h3>
          <p className="text-muted-foreground text-sm">
            Monitor your learning journey with detailed statistics and progress
            tracking.
          </p>
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center max-w-2xl mx-auto">
        <h2 className="text-2xl sm:text-3xl font-bold mb-4">
          Ready to start learning?
        </h2>
        <p className="text-muted-foreground mb-6">
          Join our community and start creating your first deck today.
        </p>
        <Link href="/decks/create">
          <Button size="lg">Create Your First Deck</Button>
        </Link>
      </div>
    </main>
  );
}
