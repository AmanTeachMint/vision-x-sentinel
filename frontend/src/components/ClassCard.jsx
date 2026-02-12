import React, { useRef, useEffect, useState } from 'react';
import { sendAudioLevel } from '../api/client';

function ClassCard({ classroom, videoUrl, onFrameCapture, hasNewAlert = false }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [useCamera, setUseCamera] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const captureIntervalRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const audioIntervalRef = useRef(null);
  const audioResumeHandlerRef = useRef(null);
  const consecutiveFailuresRef = useRef(0);
  const retryCheckIntervalRef = useRef(null);
  const onFrameCaptureRef = useRef(onFrameCapture);
  const isSeekingRef = useRef(false);
  const cameraStreamRef = useRef(null);
  const MAX_CONSECUTIVE_FAILURES = 3;
  const RETRY_CHECK_INTERVAL = 5000;

  onFrameCaptureRef.current = onFrameCapture;

  // Handle camera stream setup/cleanup
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (useCamera) {
      // Request camera access
      const enableCamera = async () => {
        try {
          setCameraError(null);
          const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'user' }, // Front camera
            audio: true
          });
          cameraStreamRef.current = stream;
          video.srcObject = stream;
          video.muted = false; // Camera audio should not be muted
          
          // Wait for video to be ready, then play
          const waitForReady = () => {
            return new Promise((resolve) => {
              if (video.readyState >= 2) {
                resolve();
              } else {
                video.addEventListener('loadedmetadata', resolve, { once: true });
              }
            });
          };
          
          await waitForReady();
          await video.play();
          
          // Ensure play event fires to start frame/audio capture
          // Use a small delay to ensure event listeners are set up
          setTimeout(() => {
            if (!video.paused && video.readyState >= 2) {
              video.dispatchEvent(new Event('play', { bubbles: true }));
            }
          }, 200);
        } catch (err) {
          console.error('Camera access failed:', err);
          setCameraError(err.message || 'Camera access denied');
          setUseCamera(false);
        }
      };
      enableCamera();
    } else {
      // Stop camera stream if switching back to video file
      if (cameraStreamRef.current) {
        cameraStreamRef.current.getTracks().forEach(track => track.stop());
        cameraStreamRef.current = null;
      }
      // Reset to video file if available
      if (videoUrl) {
        video.srcObject = null;
        video.src = videoUrl;
        video.muted = true; // Video files start muted for autoplay
      }
    }

    return () => {
      // Cleanup camera stream on unmount
      if (cameraStreamRef.current) {
        cameraStreamRef.current.getTracks().forEach(track => track.stop());
        cameraStreamRef.current = null;
      }
    };
  }, [useCamera, classroom.id, videoUrl]);

  // Auto-play video when it loads (only for video files, not camera)
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !videoUrl || useCamera) return;

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
  }, [classroom.id, videoUrl, useCamera]);

  // Start/stop frame capture and audio when video plays/pauses
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    
    // If camera is active and video is playing, ensure capture starts
    if (useCamera && !video.paused && video.readyState >= 2) {
      // Small delay to ensure everything is ready
      const timer = setTimeout(() => {
        if (!captureIntervalRef.current && !audioIntervalRef.current) {
          handlePlay();
        }
      }, 100);
      return () => clearTimeout(timer);
    }

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
          }
          // Always read from analyser (when context is running we get real level; when suspended we get 0)
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
            const fn = onFrameCaptureRef.current;
            if (fn && frameBase64) {
              try {
                await fn(classroom.id, frameBase64);
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
                          const fn = onFrameCaptureRef.current;
                          if (fn && frameBase64) {
                            await fn(classroom.id, frameBase64);
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
      
      // Stop camera stream if active
      if (cameraStreamRef.current) {
        cameraStreamRef.current.getTracks().forEach(track => track.stop());
        cameraStreamRef.current = null;
      }
    };

    const handleSeeking = () => {
      isSeekingRef.current = true;
    };
    
    const handleSeeked = () => {
      isSeekingRef.current = false;
      // After seeking completes, if video is playing, ensure capture is running
      if (!video.paused && video.readyState >= 2) {
        // Check if intervals are already running
        if (!captureIntervalRef.current && !audioIntervalRef.current) {
          handlePlay();
        }
      }
    };
    
    const handlePause = () => {
      // Don't cleanup if we're seeking (video will resume after seek)
      if (!isSeekingRef.current) {
        cleanup();
      }
    };
    
    const handleEnded = () => cleanup();

    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('ended', handleEnded);
    video.addEventListener('seeking', handleSeeking);
    video.addEventListener('seeked', handleSeeked);

    // Check if video is already playing (for camera or autoplay)
    let playTimer = null;
    if (!video.paused && video.readyState >= 2) {
      // Small delay to ensure everything is initialized
      playTimer = setTimeout(() => {
        if (!captureIntervalRef.current && !audioIntervalRef.current) {
          handlePlay();
        }
      }, 100);
    }

    return () => {
      if (playTimer) clearTimeout(playTimer);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('ended', handleEnded);
      video.removeEventListener('seeking', handleSeeking);
      video.removeEventListener('seeked', handleSeeked);
      cleanup();
    };
  }, [classroom.id, useCamera]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'inactive': return 'bg-orange-500';
      case 'empty': return 'bg-yellow-500';
      case 'mischief': return 'bg-red-500';
      case 'missing_teacher': return 'bg-amber-500';
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
          <button
            onClick={() => setUseCamera(!useCamera)}
            className={`text-xs px-2 py-1 rounded transition-colors ${
              useCamera 
                ? 'bg-green-600 hover:bg-green-700 text-white' 
                : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
            }`}
            title={useCamera ? 'Switch to video file' : 'Use live camera'}
          >
            {useCamera ? '📹 Live' : '📷 Camera'}
          </button>
          <span className={`w-2 h-2 rounded-full ${getStatusColor(classroom.current_status)}`}></span>
          <span className="text-sm text-gray-400 capitalize">{classroom.current_status}</span>
        </div>
      </div>

      <div className="relative">
        {cameraError && (
          <div className="w-full bg-red-900/50 border border-red-700 rounded-md p-3 mb-2">
            <p className="text-red-300 text-xs">Camera error: {cameraError}</p>
            <p className="text-red-400 text-xs mt-1">Please allow camera access or switch back to video file.</p>
          </div>
        )}
        {(finalVideoUrl || useCamera) ? (
          <video
            ref={videoRef}
            src={useCamera ? undefined : finalVideoUrl}
            crossOrigin={useCamera ? undefined : "anonymous"}
            className="w-full rounded-md"
            controls={!useCamera}
            playsInline
            muted={useCamera ? false : true}
            autoPlay
            loop={useCamera ? false : true}
            style={{ maxHeight: '240px' }}
          />
        ) : (
          <div className="w-full bg-gray-800 rounded-md flex flex-col items-center justify-center py-8 px-4" style={{ maxHeight: '240px', minHeight: '180px' }}>
            {/* Orange WiFi icon with slash */}
            <svg className="w-12 h-12 mb-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              {/* WiFi signal waves */}
              <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.07 2.93 1 9z" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
              <path d="M5 13l2 2c2.76-2.76 7.24-2.76 10 0l2-2c-4.01-4.01-10.99-4.01-15 0z" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
              <path d="M9 17l2 2c.55-.55 1.45-.55 2 0l2-2" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
              {/* Diagonal slash */}
              <line x1="2" y1="2" x2="22" y2="22" stroke="#f97316" strokeWidth="2.5" strokeLinecap="round"/>
            </svg>
            <p className="text-white font-semibold text-base mb-2 text-center">Device is offline</p>
            <p className="text-gray-400 text-xs text-center leading-relaxed">
              Please check that it's on the same network and updated to firmware version v1.0.9 or above.
            </p>
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
