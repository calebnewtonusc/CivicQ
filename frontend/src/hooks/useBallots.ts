import { useQuery } from '@tanstack/react-query';
import { ballotAPI, contestAPI } from '../services/api';

export const useBallots = (params?: { city_id?: string; is_published?: boolean }) => {
  return useQuery({
    queryKey: ['ballots', params],
    queryFn: () => ballotAPI.getAll(params),
  });
};

export const useBallot = (ballotId: number | undefined) => {
  return useQuery({
    queryKey: ['ballots', ballotId],
    queryFn: () => ballotAPI.getById(ballotId!),
    enabled: !!ballotId,
  });
};

export const useBallotByCityAndDate = (
  cityId: string | undefined,
  electionDate: string | undefined
) => {
  return useQuery({
    queryKey: ['ballots', 'city', cityId, 'date', electionDate],
    queryFn: () => ballotAPI.getByCityAndDate(cityId!, electionDate!),
    enabled: !!cityId && !!electionDate,
  });
};

export const useContest = (contestId: number | undefined) => {
  return useQuery({
    queryKey: ['contests', contestId],
    queryFn: () => contestAPI.getById(contestId!),
    enabled: !!contestId,
  });
};

export const useContestCandidates = (contestId: number | undefined) => {
  return useQuery({
    queryKey: ['contests', contestId, 'candidates'],
    queryFn: () => contestAPI.getCandidates(contestId!),
    enabled: !!contestId,
  });
};
