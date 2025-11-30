export type TLearnSession = {
  id: number;
  deck_id: number;
  status: string;
  total_cards: number;
  learned_cards: number;
};

export type TLearnSessionResponse = TLearnSession & {
  started_at: string;
  ended_at?: string | null;
};

export type TLearnSessionCreateResponse = {
  session: TLearnSessionResponse;
  progress: number;
};

export type TLearnBatchResponse = {
  session_id: number;
  card_id?: number | null;
  learned_cards: number;
  total_cards: number;
  progress: number;
};

export type TLearnAnswer = {
  correct: boolean;
  answer_time_seconds: number;
};

export type TLearnProgressResponse = {
  session_id: number;
  learned_cards: number;
  total_cards: number;
  progress: number;
  is_completed: boolean;
};

