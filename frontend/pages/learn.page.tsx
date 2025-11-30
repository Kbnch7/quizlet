'use client';

import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Card,
  useDeck,
  useFinishSession,
  useLearnProgress,
  useNextCard,
  useStartLearnSession,
  useSubmitAnswer,
} from '@/features/cards';
import { AccessibleIcon } from '@radix-ui/react-accessible-icon';
import { Check, RotateCcw, X } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export function LearnPage({ deckId }: { deckId: string }) {
  const deckIdNum = parseInt(deckId, 10);
  const router = useRouter();
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [currentCardId, setCurrentCardId] = useState<number | null>(null);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [answered, setAnswered] = useState(false);

  const { data: deck } = useDeck(deckIdNum);
  const startSession = useStartLearnSession(deckIdNum);
  const { data: nextCardData, refetch: refetchNext } = useNextCard(sessionId!);
  const { data: progress } = useLearnProgress(sessionId!);
  const submitAnswer = useSubmitAnswer();
  const finishSession = useFinishSession();

  useEffect(() => {
    if (!startSession.isPending && !sessionId) {
      startSession.mutate(undefined, {
        onSuccess: (data) => {
          setSessionId(data.session.id);
        },
      });
    }
  }, [startSession, sessionId]);

  useEffect(() => {
    if (sessionId && !currentCardId && !nextCardData) {
      refetchNext();
    }
  }, [sessionId, currentCardId, nextCardData, refetchNext]);

  useEffect(() => {
    if (nextCardData?.card_id) {
      setCurrentCardId(nextCardData.card_id);
      setStartTime(Date.now());
      setAnswered(false);
    }
  }, [nextCardData]);

  const handleAnswer = async (correct: boolean) => {
    if (!sessionId || !currentCardId || !startTime || answered) return;

    const answerTime = Math.floor((Date.now() - startTime) / 1000);
    setAnswered(true);

    submitAnswer.mutate(
      {
        sessionId,
        cardId: currentCardId,
        answer: {
          correct,
          answer_time_seconds: answerTime,
        },
      },
      {
        onSuccess: (progressData) => {
          if (progressData.is_completed) {
            finishSession.mutate(sessionId, {
              onSuccess: () => {
                router.push(`/decks/${deckId}/learn/complete`);
              },
            });
          } else {
            // Get next card
            setTimeout(() => {
              setCurrentCardId(null);
              refetchNext();
            }, 1000);
          }
        },
      },
    );
  };

  if (!deck) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Skeleton className="h-96" />
      </div>
    );
  }

  const currentCard = deck.cards.find((c) => c.id === currentCardId);

  return (
    <div className="container mx-auto px-4 py-4 sm:py-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-xl sm:text-2xl font-bold mb-2">{deck.title} - Learn Mode</h1>
        {progress && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">
                Progress: {progress.learned_cards} / {progress.total_cards}
              </span>
              <span className="text-sm font-semibold">
                {Math.round(progress.progress * 100)}%
              </span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress.progress * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-col items-center justify-center min-h-[400px] gap-8">
        {!currentCard ? (
          <div className="text-center">
            <Skeleton className="h-96 w-full max-w-md" />
            <p className="mt-4 text-muted-foreground">Loading next card...</p>
          </div>
        ) : (
          <>
            <div className="w-full max-w-md">
              <Card card={currentCard} />
            </div>

            {!answered && (
              <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 w-full sm:w-auto">
                <Button
                  variant="destructive"
                  size="lg"
                  onClick={() => handleAnswer(false)}
                  disabled={submitAnswer.isPending}
                  className="flex-1 sm:flex-initial"
                >
                  <AccessibleIcon label="Don't know">
                    <X className="mr-2 h-4 w-4" />
                  </AccessibleIcon>
                  <span className="hidden sm:inline">Don't know</span>
                  <span className="sm:hidden">No</span>
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => handleAnswer(false)}
                  disabled={submitAnswer.isPending}
                  className="flex-1 sm:flex-initial"
                >
                  <AccessibleIcon label="Need to review">
                    <RotateCcw className="mr-2 h-4 w-4" />
                  </AccessibleIcon>
                  <span className="hidden sm:inline">Review</span>
                  <span className="sm:hidden">Review</span>
                </Button>
                <Button
                  variant="default"
                  size="lg"
                  onClick={() => handleAnswer(true)}
                  disabled={submitAnswer.isPending}
                  className="flex-1 sm:flex-initial"
                >
                  <AccessibleIcon label="Know">
                    <Check className="mr-2 h-4 w-4" />
                  </AccessibleIcon>
                  <span className="hidden sm:inline">Know</span>
                  <span className="sm:hidden">Yes</span>
                </Button>
              </div>
            )}

            {answered && <p className="text-muted-foreground">Processing...</p>}
          </>
        )}
      </div>

      <div className="mt-8 text-center">
        <Button
          variant="outline"
          onClick={() => {
            if (sessionId) {
              finishSession.mutate(sessionId, {
                onSuccess: () => {
                  router.push(`/decks/${deckId}`);
                },
              });
            } else {
              router.push(`/decks/${deckId}`);
            }
          }}
        >
          Exit Learn Mode
        </Button>
      </div>
    </div>
  );
}
