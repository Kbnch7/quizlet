export type TCardResult = {
  id: number;
  card_id: number;
  correct: boolean;
  answer_time_seconds: number;
  user_answer?: string | null;
};

export type TCardResultCreate = {
  card_id: number;
  correct: boolean;
  answer_time_seconds: number;
  user_answer?: string | null;
};

export type TTestResult = {
  id: number;
  deck_id: number;
  user_id: number;
  total_time_seconds: number;
  correct_rate: number;
  card_results: TCardResult[];
};

export type TTestResultCreate = {
  user_id: number;
  total_time_seconds: number;
  correct_rate: number;
  card_results: TCardResultCreate[];
};

