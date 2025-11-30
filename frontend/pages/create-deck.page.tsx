'use client';

import { FormItem } from '@/components/form-item';
import { Button } from '@/components/ui/button';
import { Form, FormField } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useCategories, useCreateDeck } from '@/features/cards';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

const createDeckSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255),
  description: z.string().max(1000).optional(),
  categories: z.array(z.string()).optional(),
});

type TCreateDeckForm = z.infer<typeof createDeckSchema>;

export function CreateDeckPage() {
  const router = useRouter();
  const { data: categories } = useCategories();
  const createDeck = useCreateDeck();
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

  const form = useForm<TCreateDeckForm>({
    resolver: zodResolver(createDeckSchema),
    defaultValues: {
      title: '',
      description: '',
      categories: [],
    },
  });

  const onSubmit = (data: TCreateDeckForm) => {
    createDeck.mutate(
      {
        ...data,
        categories:
          selectedCategories.length > 0 ? selectedCategories : undefined,
      },
      {
        onSuccess: (deck) => {
          router.push(`/decks/${deck.id}`);
        },
      },
    );
  };

  return (
    <div className="container mx-auto px-4 py-4 sm:py-8 max-w-2xl">
      <h1 className="text-2xl sm:text-3xl font-bold mb-6">Create New Deck</h1>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="title"
            render={({ field }) => (
              <FormItem label="Title">
                <Input placeholder="Enter deck title" {...field} />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem label="Description" description="Optional">
                <Textarea
                  placeholder="Enter deck description"
                  {...field}
                  rows={4}
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

          <div className="flex gap-2">
            <Button type="submit" disabled={createDeck.isPending}>
              {createDeck.isPending ? 'Creating...' : 'Create Deck'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
            >
              Cancel
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
