/**
 * Unit tests for QuestionCard component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QuestionCard } from '../../components/QuestionCard';

// Mock question data
const mockQuestion = {
  id: 1,
  text: 'What is your plan for affordable housing?',
  issueTags: ['housing', 'economy'],
  voteCount: 42,
  createdAt: '2024-02-01T00:00:00Z',
  author: 'John Voter',
  contestId: 1,
};

describe('QuestionCard', () => {
  it('renders question text correctly', () => {
    render(<QuestionCard question={mockQuestion} />);

    expect(screen.getByText(mockQuestion.text)).toBeInTheDocument();
  });

  it('displays vote count', () => {
    render(<QuestionCard question={mockQuestion} />);

    expect(screen.getByText(/42/)).toBeInTheDocument();
  });

  it('renders issue tags', () => {
    render(<QuestionCard question={mockQuestion} />);

    mockQuestion.issueTags.forEach((tag) => {
      expect(screen.getByText(tag)).toBeInTheDocument();
    });
  });

  it('calls upvote handler when upvote button clicked', async () => {
    const onUpvote = jest.fn();
    render(<QuestionCard question={mockQuestion} onUpvote={onUpvote} />);

    const upvoteButton = screen.getByLabelText('Upvote question');
    fireEvent.click(upvoteButton);

    await waitFor(() => {
      expect(onUpvote).toHaveBeenCalledWith(mockQuestion.id);
    });
  });

  it('calls downvote handler when downvote button clicked', async () => {
    const onDownvote = jest.fn();
    render(<QuestionCard question={mockQuestion} onDownvote={onDownvote} />);

    const downvoteButton = screen.getByLabelText('Downvote question');
    fireEvent.click(downvoteButton);

    await waitFor(() => {
      expect(onDownvote).toHaveBeenCalledWith(mockQuestion.id);
    });
  });

  it('shows answer count when answers exist', () => {
    const questionWithAnswers = {
      ...mockQuestion,
      answerCount: 3,
    };

    render(<QuestionCard question={questionWithAnswers} />);

    expect(screen.getByText(/3 answers/i)).toBeInTheDocument();
  });

  it('navigates to question detail when clicked', () => {
    const onNavigate = jest.fn();
    render(<QuestionCard question={mockQuestion} onNavigate={onNavigate} />);

    const card = screen.getByRole('article');
    fireEvent.click(card);

    expect(onNavigate).toHaveBeenCalledWith(mockQuestion.id);
  });

  it('highlights question when selected', () => {
    render(<QuestionCard question={mockQuestion} isSelected={true} />);

    const card = screen.getByRole('article');
    expect(card).toHaveClass('selected');
  });

  it('displays "No answers yet" when no answers exist', () => {
    const questionNoAnswers = {
      ...mockQuestion,
      answerCount: 0,
    };

    render(<QuestionCard question={questionNoAnswers} />);

    expect(screen.getByText(/no answers yet/i)).toBeInTheDocument();
  });
});
