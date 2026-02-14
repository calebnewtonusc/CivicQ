/**
 * Unit tests for AnswerVideo component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AnswerVideo } from '../../components/AnswerVideo';

const mockAnswer = {
  id: 1,
  questionId: 1,
  candidateId: 1,
  candidateName: 'Jane Candidate',
  videoUrl: 'https://example.com/video.mp4',
  transcript: 'This is my answer to the housing question...',
  duration: 90,
  createdAt: '2024-02-01T00:00:00Z',
};

// Mock HTML5 video element
beforeAll(() => {
  window.HTMLMediaElement.prototype.play = jest.fn();
  window.HTMLMediaElement.prototype.pause = jest.fn();
  window.HTMLMediaElement.prototype.load = jest.fn();
});

describe('AnswerVideo', () => {
  it('renders video player with correct source', () => {
    render(<AnswerVideo answer={mockAnswer} />);

    const video = screen.getByTestId('answer-video');
    expect(video).toHaveAttribute('src', mockAnswer.videoUrl);
  });

  it('displays candidate name', () => {
    render(<AnswerVideo answer={mockAnswer} />);

    expect(screen.getByText(mockAnswer.candidateName)).toBeInTheDocument();
  });

  it('shows captions/transcript toggle', () => {
    render(<AnswerVideo answer={mockAnswer} />);

    const captionsButton = screen.getByLabelText(/show captions/i);
    expect(captionsButton).toBeInTheDocument();
  });

  it('displays transcript when captions enabled', async () => {
    render(<AnswerVideo answer={mockAnswer} />);

    const captionsButton = screen.getByLabelText(/show captions/i);
    fireEvent.click(captionsButton);

    await waitFor(() => {
      expect(screen.getByText(mockAnswer.transcript)).toBeInTheDocument();
    });
  });

  it('shows video controls', () => {
    render(<AnswerVideo answer={mockAnswer} />);

    const playButton = screen.getByLabelText(/play/i);
    const volumeControl = screen.getByLabelText(/volume/i);
    const fullscreenButton = screen.getByLabelText(/fullscreen/i);

    expect(playButton).toBeInTheDocument();
    expect(volumeControl).toBeInTheDocument();
    expect(fullscreenButton).toBeInTheDocument();
  });

  it('plays video when play button clicked', async () => {
    render(<AnswerVideo answer={mockAnswer} />);

    const playButton = screen.getByLabelText(/play/i);
    fireEvent.click(playButton);

    const video = screen.getByTestId('answer-video') as HTMLVideoElement;
    await waitFor(() => {
      expect(video.play).toHaveBeenCalled();
    });
  });

  it('displays video duration', () => {
    render(<AnswerVideo answer={mockAnswer} />);

    expect(screen.getByText(/1:30/)).toBeInTheDocument(); // 90 seconds = 1:30
  });

  it('shows loading state while video loads', () => {
    render(<AnswerVideo answer={mockAnswer} />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('displays error message on video load failure', async () => {
    render(<AnswerVideo answer={mockAnswer} />);

    const video = screen.getByTestId('answer-video');
    fireEvent.error(video);

    await waitFor(() => {
      expect(screen.getByText(/failed to load video/i)).toBeInTheDocument();
    });
  });

  it('tracks video watch time', async () => {
    const onWatchProgress = jest.fn();
    render(<AnswerVideo answer={mockAnswer} onWatchProgress={onWatchProgress} />);

    const video = screen.getByTestId('answer-video');

    // Simulate video time update
    Object.defineProperty(video, 'currentTime', { value: 45, writable: true });
    fireEvent.timeUpdate(video);

    await waitFor(() => {
      expect(onWatchProgress).toHaveBeenCalledWith(
        expect.objectContaining({
          answerId: mockAnswer.id,
          watchedSeconds: 45,
        })
      );
    });
  });

  it('provides download transcript link', () => {
    render(<AnswerVideo answer={mockAnswer} showTranscriptDownload={true} />);

    const downloadLink = screen.getByText(/download transcript/i);
    expect(downloadLink).toBeInTheDocument();
    expect(downloadLink).toHaveAttribute('download');
  });
});
