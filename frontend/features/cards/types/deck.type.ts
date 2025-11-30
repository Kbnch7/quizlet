import type { TCard } from './card.type';

export type TCategory = {
  id: number;
  name: string;
  slug: string;
};

export type TTag = {
  id: number;
  name: string;
  slug: string;
};

export type TDeck = {
  id: number;
  owner_id: number;
  title: string;
  description?: string | null;
  cards_amount: number;
  categories?: TCategory[] | null;
  tags?: TTag[] | null;
};

export type TDeckDetailed = TDeck & {
  cards: TCard[];
};

export type TDeckCreate = {
  title: string;
  owner_id?: number | null;
  description?: string | null;
  categories?: string[] | null;
  tags?: string[] | null;
};

export type TDeckUpdate = {
  title?: string;
  owner_id?: number | null;
  description?: string | null;
  categories?: string[] | null;
  tags?: string[] | null;
};

export type TDeckListParams = {
  author?: number;
  category?: string;
  tag?: string;
  my_teachers?: boolean;
  cursor?: number;
  limit?: number;
};

