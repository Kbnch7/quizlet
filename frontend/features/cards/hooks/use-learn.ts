import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { learnApi } from '../api/learn.api';
import type { TLearnAnswer } from '../types/learn.type';

export const learnKeys = {
  all: ['learn'] as const,
  sessions: () => [...learnKeys.all, 'sessions'] as const,
  session: (id: number) => [...learnKeys.sessions(), id] as const,
  progress: (id: number) => [...learnKeys.session(id), 'progress'] as const,
  next: (id: number) => [...learnKeys.session(id), 'next'] as const,
};

export function useStartLearnSession(deckId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => learnApi.startSession(deckId),
    onSuccess: (data) => {
      queryClient.setQueryData(learnKeys.session(data.session.id), data.session);
    },
  });
}

export function useLearnSession(sessionId: number) {
  return useQuery({
    queryKey: learnKeys.session(sessionId),
    queryFn: () => learnApi.getSession(sessionId),
    enabled: !!sessionId,
  });
}

export function useNextCard(sessionId: number) {
  return useQuery({
    queryKey: learnKeys.next(sessionId),
    queryFn: () => learnApi.getNextCard(sessionId),
    enabled: !!sessionId,
  });
}

export function useSubmitAnswer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      sessionId,
      cardId,
      answer,
    }: {
      sessionId: number;
      cardId: number;
      answer: TLearnAnswer;
    }) => learnApi.submitAnswer(sessionId, cardId, answer),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({
        queryKey: learnKeys.session(variables.sessionId),
      });
      queryClient.invalidateQueries({
        queryKey: learnKeys.progress(variables.sessionId),
      });
      queryClient.invalidateQueries({
        queryKey: learnKeys.next(variables.sessionId),
      });
    },
  });
}

export function useLearnProgress(sessionId: number) {
  return useQuery({
    queryKey: learnKeys.progress(sessionId),
    queryFn: () => learnApi.getProgress(sessionId),
    enabled: !!sessionId,
    refetchInterval: 5000, // Refetch every 5 seconds
  });
}

export function useFinishSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: number) => learnApi.finishSession(sessionId),
    onSuccess: (data, sessionId) => {
      queryClient.invalidateQueries({
        queryKey: learnKeys.session(sessionId),
      });
      queryClient.invalidateQueries({
        queryKey: learnKeys.progress(sessionId),
      });
    },
  });
}

