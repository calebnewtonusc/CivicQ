import React from 'react';
import ReactPlayer from 'react-player';
import { VideoAnswer } from '../types';

interface VideoPlayerProps {
  answer: VideoAnswer;
  controls?: boolean;
  width?: string;
  height?: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  answer,
  controls = true,
  width = '100%',
  height = 'auto',
}) => {
  if (!answer.video_url) {
    return (
      <div className="bg-gray-100 rounded-lg p-8 text-center text-gray-500">
        Video not available
      </div>
    );
  }

  return (
    <div className="rounded-lg overflow-hidden bg-black">
      <ReactPlayer
        url={answer.video_url}
        controls={controls}
        width={width}
        height={height}
        config={{
          file: {
            attributes: {
              controlsList: 'nodownload',
            },
            tracks: answer.captions_url
              ? [
                  {
                    kind: 'subtitles',
                    src: answer.captions_url,
                    srcLang: 'en',
                    label: 'English',
                    default: true,
                  },
                ]
              : undefined,
          },
        }}
      />

      {/* Video Info */}
      <div className="bg-white p-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Duration: {Math.floor(answer.duration / 60)}:{(answer.duration % 60).toFixed(0).padStart(2, '0')}</span>
          <span
            className={`px-2 py-1 rounded text-xs font-medium ${
              answer.status === 'published'
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {answer.status}
          </span>
        </div>

        {/* Position Summary */}
        {answer.position_summary && (
          <div className="mt-3">
            <h4 className="text-sm font-semibold text-gray-900">Summary</h4>
            <p className="mt-1 text-sm text-gray-700">{answer.position_summary}</p>
          </div>
        )}

        {/* Open Question Flag */}
        {answer.is_open_question && (
          <div className="mt-3 bg-blue-50 border border-blue-200 rounded-md p-3">
            <p className="text-sm text-blue-800">
              This candidate indicated they are still forming their opinion on this question.
            </p>
          </div>
        )}

        {/* Correction */}
        {answer.has_correction && answer.correction_text && (
          <div className="mt-3 bg-yellow-50 border border-yellow-200 rounded-md p-3">
            <h4 className="text-sm font-semibold text-yellow-900">Correction</h4>
            <p className="mt-1 text-sm text-yellow-800">{answer.correction_text}</p>
          </div>
        )}
      </div>

      {/* Transcript */}
      {answer.transcript_text && (
        <details className="bg-gray-50 border-t border-gray-200">
          <summary className="px-4 py-3 cursor-pointer text-sm font-medium text-gray-700 hover:bg-gray-100">
            View Transcript
          </summary>
          <div className="px-4 py-3 text-sm text-gray-700 whitespace-pre-wrap">
            {answer.transcript_text}
          </div>
        </details>
      )}
    </div>
  );
};

export default VideoPlayer;
