'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useDeck, useUpdateDeck, useCreateCard, useUpdateCard, useDeleteCard } from '@/features/cards';
import { useCategories } from '@/features/cards';
import { Form, FormField } from '@/components/ui/form';
import { FormItem } from '@/components/form-item';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import type { TCard } from '@/features/cards';
import { Trash2, Plus, Save } from 'lucide-react';
import { AccessibleIcon } from '@radix-ui/react-accessible-icon';

const deckSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255),
  description: z.string().max(1000).optional(),
});

const cardSchema = z.object({
  front_text: z.string().min(1, 'Front text is required'),
  back_text: z.string().min(1, 'Back text is required'),
});

type TDeckForm = z.infer<typeof deckSchema>;
type TCardForm = z.infer<typeof cardSchema>;

export function EditDeckPage({ deckId }: { deckId: string }) {
  const deckIdNum = parseInt(deckId, 10);
  const router = useRouter();
  const { data: deck, isLoading } = useDeck(deckIdNum);
  const { data: categories } = useCategories();
  const updateDeck = useUpdateDeck();
  const createCard = useCreateCard(deckIdNum);
  const updateCard = useUpdateCard(deckIdNum);
  const deleteCard = useDeleteCard(deckIdNum);

  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [editingCardId, setEditingCardId] = useState<number | null>(null);
  const [newCard, setNewCard] = useState<TCardForm | null>(null);

  const deckForm = useForm<TDeckForm>({
    resolver: zodResolver(deckSchema),
    defaultValues: {
      title: deck?.title || '',
      description: deck?.description || '',
    },
    values: deck
      ? {
          title: deck.title,
          description: deck.description || '',
        }
      : undefined,
  });

  const cardForm = useForm<TCardForm>({
    resolver: zodResolver(cardSchema),
  });

  // Initialize selected categories when deck loads
  useEffect(() => {
    if (deck?.categories && selectedCategories.length === 0) {
      setSelectedCategories(deck.categories.map((c) => c.slug));
    }
  }, [deck, selectedCategories.length]);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-4 sm:py-8 max-w-4xl">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/3" />
          <div className="h-32 bg-muted rounded" />
        </div>
      </div>
    );
  }

  if (!deck) {
    return (
      <div className="container mx-auto px-4 py-4 sm:py-8 max-w-4xl">
        <p className="text-destructive">Deck not found</p>
      </div>
    );
  }

  const handleDeckSubmit = (data: TDeckForm) => {
    updateDeck.mutate(
      {
        deckId: deckIdNum,
        data: {
          ...data,
          categories: selectedCategories.length > 0 ? selectedCategories : undefined,
        },
      },
      {
        onSuccess: () => {
          router.push(`/decks/${deckId}`);
        },
      },
    );
  };

  const handleCardSubmit = (data: TCardForm, card?: TCard) => {
    if (card) {
      updateCard.mutate(
        {
          cardId: card.id,
          data,
        },
        {
          onSuccess: () => {
            setEditingCardId(null);
            cardForm.reset();
          },
        },
      );
    } else {
      createCard.mutate(
        {
          ...data,
          order_index: deck.cards.length,
        },
        {
          onSuccess: () => {
            setNewCard(null);
            cardForm.reset();
          },
        },
      );
    }
  };

  const handleDeleteCard = (cardId: number) => {
    if (confirm('Are you sure you want to delete this card?')) {
      deleteCard.mutate(cardId);
    }
  };

  return (
    <div className="container mx-auto px-4 py-4 sm:py-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold mb-4">Edit Deck</h1>

        <Form {...deckForm}>
          <form
            onSubmit={deckForm.handleSubmit(handleDeckSubmit)}
            className="space-y-4 mb-6"
          >
            <FormField
              control={deckForm.control}
              name="title"
              render={({ field }) => (
                <FormItem label="Title">
                  <Input placeholder="Enter deck title" {...field} />
                </FormItem>
              )}
            />

            <FormField
              control={deckForm.control}
              name="description"
              render={({ field }) => (
                <FormItem label="Description" description="Optional">
                  <Textarea
                    placeholder="Enter deck description"
                    {...field}
                    rows={3}
                  />
                </FormItem>
              )}
            />

            {categories && categories.length > 0 && (
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Categories
                </label>
                <div className="flex flex-wrap gap-2">
                  {categories.map((category) => (
                    <Button
                      key={category.id}
                      type="button"
                      variant={
                        selectedCategories.includes(category.slug)
                          ? 'default'
                          : 'outline'
                      }
                      size="sm"
                      onClick={() => {
                        setSelectedCategories((prev) =>
                          prev.includes(category.slug)
                            ? prev.filter((c) => c !== category.slug)
                            : [...prev, category.slug],
                        );
                      }}
                    >
                      {category.name}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-2 flex-wrap">
              <Button
                type="submit"
                disabled={updateDeck.isPending}
                className="flex-1 sm:flex-initial"
              >
                <Save className="mr-2 h-4 w-4" />
                Save Deck
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                className="flex-1 sm:flex-initial"
              >
                Cancel
              </Button>
            </div>
          </form>
        </Form>
      </div>

        <div className="mb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
            <h2 className="text-xl sm:text-2xl font-semibold">
              Cards ({deck.cards.length})
            </h2>
            <Button
              onClick={() => setNewCard({ front_text: '', back_text: '' })}
              size="sm"
              className="flex items-center gap-2 w-full sm:w-auto"
            >
              <Plus className="h-4 w-4" />
              <span>Add Card</span>
            </Button>
          </div>

        {newCard && (
          <div className="mb-4 p-4 border rounded-lg bg-muted/50">
            <Form {...cardForm}>
              <form
                onSubmit={cardForm.handleSubmit((data) =>
                  handleCardSubmit(data),
                )}
                className="space-y-4"
              >
                <FormField
                  control={cardForm.control}
                  name="front_text"
                  render={({ field }) => (
                    <FormItem label="Front">
                      <Textarea
                        placeholder="Enter front text"
                        {...field}
                        rows={2}
                      />
                    </FormItem>
                  )}
                />
                <FormField
                  control={cardForm.control}
                  name="back_text"
                  render={({ field }) => (
                    <FormItem label="Back">
                      <Textarea
                        placeholder="Enter back text"
                        {...field}
                        rows={2}
                      />
                    </FormItem>
                  )}
                />
                <div className="flex gap-2 flex-wrap">
                  <Button
                    type="submit"
                    size="sm"
                    disabled={createCard.isPending}
                    className="flex-1 sm:flex-initial"
                  >
                    Save
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setNewCard(null);
                      cardForm.reset();
                    }}
                    className="flex-1 sm:flex-initial"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </Form>
          </div>
        )}

        <div className="space-y-4">
          {deck.cards.map((card) => (
            <div
              key={card.id}
              className="p-4 border rounded-lg hover:shadow-md transition-shadow"
            >
              {editingCardId === card.id ? (
                <Form {...cardForm}>
                  <form
                    onSubmit={cardForm.handleSubmit((data) =>
                      handleCardSubmit(data, card),
                    )}
                    className="space-y-4"
                  >
                    <FormField
                      control={cardForm.control}
                      name="front_text"
                      defaultValue={card.front_text}
                      render={({ field }) => (
                        <FormItem label="Front">
                          <Textarea
                            placeholder="Enter front text"
                            {...field}
                            rows={2}
                          />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={cardForm.control}
                      name="back_text"
                      defaultValue={card.back_text}
                      render={({ field }) => (
                        <FormItem label="Back">
                          <Textarea
                            placeholder="Enter back text"
                            {...field}
                            rows={2}
                          />
                        </FormItem>
                      )}
                    />
                    <div className="flex gap-2 flex-wrap">
                      <Button
                        type="submit"
                        size="sm"
                        disabled={updateCard.isPending}
                        className="flex-1 sm:flex-initial"
                      >
                        Save
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setEditingCardId(null);
                          cardForm.reset();
                        }}
                        className="flex-1 sm:flex-initial"
                      >
                        Cancel
                      </Button>
                    </div>
                  </form>
                </Form>
              ) : (
                <div className="space-y-2">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Front:</p>
                    <p className="text-base">{card.front_text}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Back:</p>
                    <p className="text-base">{card.back_text}</p>
                  </div>
                  <div className="flex gap-2 pt-2 flex-wrap">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditingCardId(card.id);
                        cardForm.reset({
                          front_text: card.front_text,
                          back_text: card.back_text,
                        });
                      }}
                      className="flex-1 sm:flex-initial"
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDeleteCard(card.id)}
                      disabled={deleteCard.isPending}
                      className="flex-1 sm:flex-initial"
                    >
                      <AccessibleIcon label="Delete">
                        <Trash2 className="h-4 w-4" />
                      </AccessibleIcon>
                      <span className="ml-2 sm:hidden">Delete</span>
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
