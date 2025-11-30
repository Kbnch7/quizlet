// Type definitions for Next.js App Router
import type { ReadonlyRequestCookies } from 'next/dist/server/web/spec-extension/adapters/request-cookies';

type RouteParams = {
  '/decks/[deckId]': { deckId: string };
  '/decks/[deckId]/learn': { deckId: string };
  '/decks/[deckId]/learn/complete': { deckId: string };
  '/decks/[deckId]/study': { deckId: string };
};

type PageProps<T extends keyof RouteParams> = {
  params: Promise<RouteParams[T]>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

declare global {
  type PageProps<T extends keyof RouteParams> = {
    params: Promise<RouteParams[T]>;
    searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
  };
}

