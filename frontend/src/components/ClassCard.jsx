import React, { useRef, useEffect, useState } from 'react';
import { sendAudioLevel } from '../api/client';

function ClassCard({ classroom, videoUrl, onFrameCapture, hasNewAlert = false }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const captureIntervalRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const audioIntervalRef = useRef(null);
  const audioResumeHandlerRef = useRef(null);
  const consecutiveFailuresRef = useRef(0);
  const retryCheckIntervalRef = useRef(null);
  const MAX_CONSECUTIVE_FAILURES = 3;
  const RETRY_CHECK_INTERVAL = 5000;

  // Auto-play video when it loads
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !videoUrl) return;

    const tryAutoPlay = async () => {
      try {
        await video.play();
        if (!video.paused) {
          video.dispatchEvent(new Event('play'));
        }
      } catch (err) {
        console.log(`Autoplay blocked for ${classroom.id}, video will play on user interaction`);
      }
    };

    if (video.readyState >= 2) {
      tryAutoPlay();
    } else {
      video.addEventListener('loadeddata', tryAutoPlay);
      return () => video.removeEventListener('loadeddata', tryAutoPlay);
    }
  }, [classroom.id, videoUrl]);

  // Start/stop frame capture and audio when video plays/pauses
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    const setupAudioCapture = () => {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;

        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;

        const source = audioContext.createMediaElementSource(video);
        source.connect(audioContext.destination);
        source.connect(analyser);

        audioContextRef.current = audioContext;
        analyserRef.current = analyser;

        const resumeOnInteraction = () => {
          if (audioContext.state === 'suspended') {
            audioContext.resume().catch(() => {});
          }
        };
        audioResumeHandlerRef.current = resumeOnInteraction;
        video.addEventListener('click', resumeOnInteraction);
        video.addEventListener('volumechange', resumeOnInteraction);
        video.addEventListener('play', resumeOnInteraction);

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        audioIntervalRef.current = setInterval(() => {
          if (audioContext.state === 'suspended') {
            audioContext.resume().catch(() => {});
            return;
          }
          analyser.getByteTimeDomainData(dataArray);
          let sum = 0;
          for (let i = 0; i < bufferLength; i++) {
            const normalized = (dataArray[i] - 128) / 128;
            sum += normalized * normalized;
          }
          const rms = Math.sqrt(sum / bufferLength);
          const level = Math.min(Math.max(rms, 0), 1);
          sendAudioLevel(classroom.id, level)
            .then(() => { /* noise API ok */ })
            .catch((err) => console.warn('Audio level API failed:', classroom.id, err.message));
        }, 1000);
      } catch (e) {
        console.warn('Audio capture setup failed:', e.message);
      }
    };

    const startFrameCapture = () => {
      consecutiveFailuresRef.current = 0;
      if (captureIntervalRef.current) clearInterval(captureIntervalRef.current);

      canvas.width = 640;
      canvas.height = 360;

      captureIntervalRef.current = setInterval(async () => {
        if (video.readyState >= 2) {
          try {
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const frameBase64 = canvas.toDataURL('image/jpeg', 0.8);
            if (onFrameCapture && frameBase64) {
              try {
                await onFrameCapture(classroom.id, frameBase64);
                consecutiveFailuresRef.current = 0;
              } catch (err) {
                consecutiveFailuresRef.current += 1;
                if (consecutiveFailuresRef.current >= MAX_CONSECUTIVE_FAILURES) {
                  if (captureIntervalRef.current) {
                    clearInterval(captureIntervalRef.current);
                    captureIntervalRef.current = null;
                  }
                  if (!retryCheckIntervalRef.current) {
                    retryCheckIntervalRef.current = setInterval(async () => {
                      if (video.readyState >= 2 && !video.paused) {
                        try {
                          const ctx = canvas.getContext('2d');
                          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                          const frameBase64 = canvas.toDataURL('image/jpeg', 0.8);
                          if (onFrameCapture && frameBase64) {
                            await onFrameCapture(classroom.id, frameBase64);
                            if (retryCheckIntervalRef.current) {
                              clearInterval(retryCheckIntervalRef.current);
                              retryCheckIntervalRef.current = null;
                            }
                            startFrameCapture();
                          }
                        } catch (_) {}
                      }
                    }, RETRY_CHECK_INTERVAL);
                  }
                }
              }
            }
          } catch (e) {
            console.warn('Frame capture failed:', e.message);
          }
        }
      }, 1500);
    };

    const handlePlay = () => {
      setIsPlaying(true);
      startFrameCapture();
      setupAudioCapture();
    };

    const cleanup = () => {
      setIsPlaying(false);
      if (captureIntervalRef.current) {
        clearInterval(captureIntervalRef.current);
        captureIntervalRef.current = null;
      }
      if (retryCheckIntervalRef.current) {
        clearInterval(retryCheckIntervalRef.current);
        retryCheckIntervalRef.current = null;
      }
      if (audioIntervalRef.current) {
        clearInterval(audioIntervalRef.current);
        audioIntervalRef.current = null;
      }
      if (audioContextRef.current) {
        const handler = audioResumeHandlerRef.current;
        if (video && handler) {
          video.removeEventListener('click', handler);
          video.removeEventListener('volumechange', handler);
          video.removeEventListener('play', handler);
        }
        audioContextRef.current.close().catch(() => {});
        audioContextRef.current = null;
      }
      audioResumeHandlerRef.current = null;
      analyserRef.current = null;
      consecutiveFailuresRef.current = 0;
    };

    const handlePause = () => cleanup();
    const handleEnded = () => cleanup();

    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('ended', handleEnded);

    if (!video.paused && video.readyState >= 2) {
      handlePlay();
    }

    return () => {
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('ended', handleEnded);
      cleanup();
    };
  }, [classroom.id, onFrameCapture]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'inactive': return 'bg-orange-500';
      case 'empty': return 'bg-yellow-500';
      case 'mischief': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const finalVideoUrl = videoUrl || null;

  return (
    <div className="bg-dark-card rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">{classroom.name}</h3>
        <div className="flex items-center gap-2">
          {hasNewAlert && (
            <span className="text-xs bg-amber-500/80 text-black px-1.5 py-0.5 rounded font-medium">New alert</span>
          )}
          <span className={`w-2 h-2 rounded-full ${getStatusColor(classroom.current_status)}`}></span>
          <span className="text-sm text-gray-400 capitalize">{classroom.current_status}</span>
        </div>
      </div>

      <div className="relative">
        {finalVideoUrl ? (
          <video
            ref={videoRef}
            src={finalVideoUrl}
            crossOrigin="anonymous"
            className="w-full rounded-md"
            controls
            playsInline
            muted
            autoPlay
            loop
            style={{ maxHeight: '240px' }}
          />
        ) : (
          <div className="w-full bg-gray-800 rounded-md flex items-center justify-center" style={{ maxHeight: '240px', minHeight: '180px' }}>
            <span className="text-gray-500">No video assigned</span>
          </div>
        )}
        <canvas ref={canvasRef} className="hidden" width="640" height="360" />
      </div>

      {isPlaying && (
        <div className="mt-2 text-xs text-green-400 flex items-center gap-1">
          <span>●</span>
          <span>Capturing frames...</span>
        </div>
      )}
    </div>
  );
}

export default ClassCard;
