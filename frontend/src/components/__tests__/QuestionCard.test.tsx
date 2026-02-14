/**
 * Tests for QuestionCard component
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import QuestionCard from '../QuestionCard';

expect.extend(toHaveNoViolations);

const mockQuestion = {
  id: 1,
  question_text: 'What is your plan for affordable housing?',
  issue_tags: ['housing', 'economy'],
  upvotes: 10,
  downvotes: 2,
  rank_score: 8.0,
  author: {
    id: 1,
    full_name: 'Test Voter',
  },
  created_at: '2024-01-15T10:00:00Z',
  status: 'approved',
};

const mockOnVote = jest.fn();
const mockOnFlag = jest.fn();

describe('QuestionCard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders question text', () => {
      render(<QuestionCard question={mockQuestion} onVote={mockOnVote} />);
      expect(screen.getByText(mockQuestion.question_text)).toBeInTheDocument();
    });

    it('displays vote counts', () => {
      render(<QuestionCard question={mockQuestion} onVote={mockOnVote} />);
      expect(screen.getByText(/10/)).toBeInTheDocument(); // upvotes
    });

    it('shows issue tags', () => {
      render(<QuestionCard question={mockQuestion} onVote={mockOnVote} />);
      expect(screen.getByText('housing')).toBeInTheDocument();
      expect(screen.getByText('economy')).toBeInTheDocument();
    });

    it('displays author name', () => {
      render(<QuestionCard question={mockQuestion} onVote={mockOnVote} />);
      expect(screen.getByText(/Test Voter/)).toBeInTheDocument();
    });

    it('shows formatted date', () => {
      render(<QuestionCard question={mockQuestion} onVote={mockOnVote} />);
      // Date should be formatted
      expect(screen.getByText(/Jan|January/)).toBeInTheDocument();
    });
  });

  describe('Voting', () => {
    it('calls onVote when upvote button is clicked', async () => {
      render(<QuestionCard question={mockQuestion} onVote={mockOnVote} />);

      const upvoteButton = screen.getByLabelText(/upvote/i);
      fireEvent.click(upvoteButton);

      await waitFor(() => {
        expect(mockOnVote).toHaveBeenCalledWith(mockQuestion.id, 1);
      });
    });

    it('calls onVote when downvote button is clicked', async () => {
      render(<QuestionCard question={mockQuestion} onVote={mockOnVote} />);

      const downvoteButton = screen.getByLabelText(/downvote/i);
      fireEvent.click(downvoteButton);

      await waitFor(() => {
        expect(mockOnVote).toHaveBeenCalledWith(mockQuestion.id, -1);
      });
    });

    it('disables voting buttons when user not authenticated', () => {
      render(
        <QuestionCard
          question={mockQuestion}
          onVote={mockOnVote}
          isAuthenticated={false}
        />
      );

      const upvoteButton = screen.getByLabelText(/upvote/i);
      expect(upvoteButton).toBeDisabled();
    });

    it('shows active state when user has upvoted', () => {
      render(
        <QuestionCard
          question={mockQuestion}
          onVote={mockOnVote}
          userVote={1}
        />
      );

      const upvoteButton = screen.getByLabelText(/upvote/i);
      expect(upvoteButton).toHaveClass('active');
    });
  });

  describe('Moderation', () => {
    it('shows flag button', () => {
      render(
        <QuestionCard
          question={mockQuestion}
          onVote={mockOnVote}
          onFlag={mockOnFlag}
        />
      );

      expect(screen.getByLabelText(/flag|report/i)).toBeInTheDocument();
    });

    it('calls onFlag when flag button is clicked', async () => {
      render(
        <QuestionCard
          question={mockQuestion}
          onVote={mockOnVote}
          onFlag={mockOnFlag}
        />
      );

      const flagButton = screen.getByLabelText(/flag|report/i);
      fireEvent.click(flagButton);

      await waitFor(() => {
        expect(mockOnFlag).toHaveBeenCalledWith(mockQuestion.id);
      });
    });

    it('shows pending status for pending questions', () => {
      const pendingQuestion = { ...mockQuestion, status: 'pending' };
      render(<QuestionCard question={pendingQuestion} onVote={mockOnVote} />);

      expect(screen.getByText(/pending/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has no accessibility violations', async () => {
      const { container } = render(
        <QuestionCard question={mockQuestion} onVote={mockOnVote} />
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('has proper button labels', () => {
      render(<QuestionCard question={mockQuestion} onVote={mockOnVote} />);

      expect(screen.getByLabelText(/upvote/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/downvote/i)).toBeInTheDocument();
    });

    it('maintains focus after voting', async () => {
      render(<QuestionCard question={mockQuestion} onVote={mockOnVote} />);

      const upvoteButton = screen.getByLabelText(/upvote/i);
      upvoteButton.focus();
      fireEvent.click(upvoteButton);

      await waitFor(() => {
        expect(upvoteButton).toHaveFocus();
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles missing author gracefully', () => {
      const questionNoAuthor = { ...mockQuestion, author: null };
      render(<QuestionCard question={questionNoAuthor} onVote={mockOnVote} />);

      expect(screen.queryByText(/Test Voter/)).not.toBeInTheDocument();
      expect(screen.getByText(/anonymous/i)).toBeInTheDocument();
    });

    it('handles zero votes', () => {
      const questionNoVotes = { ...mockQuestion, upvotes: 0, downvotes: 0 };
      render(<QuestionCard question={questionNoVotes} onVote={mockOnVote} />);

      expect(screen.getByText('0')).toBeInTheDocument();
    });

    it('handles empty tags array', () => {
      const questionNoTags = { ...mockQuestion, issue_tags: [] };
      render(<QuestionCard question={questionNoTags} onVote={mockOnVote} />);

      expect(screen.queryByRole('list')).not.toBeInTheDocument();
    });
  });
});
