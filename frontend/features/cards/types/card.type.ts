export type TCard = {
  id: number;
  deck_id: number;
  front_text: string;
  front_image_url?: string | null;
  back_text: string;
  back_image_url?: string | null;
  order_index?: number;
};

export type TCardCreate = {
  front_text: string;
  front_image_url?: string | null;
  back_text: string;
  back_image_url?: string | null;
  order_index?: number;
};

export type TCardUpdate = {
  front_text?: string;
  front_image_url?: string | null;
  back_text?: string;
  back_image_url?: string | null;
  order_index?: number;
};

export type TCardBulkItem = {
  id?: number;
  front_text?: string;
  front_image_url?: string | null;
  back_text?: string;
  back_image_url?: string | null;
  order_index?: number;
  to_delete?: boolean;
};
