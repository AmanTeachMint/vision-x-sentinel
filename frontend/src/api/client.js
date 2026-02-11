/** API client for Vision X Sentinel backend. */
const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Get all classrooms.
 * @returns {Promise<Array>} List of classrooms
 */
export async function getClassrooms() {
  const response = await fetch(`${API_BASE_URL}/classrooms`);
  if (!response.ok) {
    throw new Error(`Failed to fetch classrooms: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get one classroom by ID.
 * @param {string} id - Classroom ID (e.g. "8A")
 * @returns {Promise<Object>} Classroom object
 */
export async function getClassroom(id) {
  const response = await fetch(`${API_BASE_URL}/classrooms/${id}`);
  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error(`Failed to fetch classroom: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get alerts, optionally filtered by classroom ID.
 * @param {string|null} classroomId - Optional classroom ID to filter
 * @returns {Promise<Array>} List of alerts
 */
export async function getAlerts(classroomId = null) {
  const url = classroomId
    ? `${API_BASE_URL}/alerts?classroom_id=${classroomId}`
    : `${API_BASE_URL}/alerts`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch alerts: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get all videos, optionally filtered by classroom ID.
 * @param {string|null} classroomId - Optional classroom ID to filter
 * @returns {Promise<Array>} List of videos
 */
export async function getVideos(classroomId = null) {
  const url = classroomId
    ? `${API_BASE_URL}/videos?classroom_id=${classroomId}`
    : `${API_BASE_URL}/videos`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch videos: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get one video by ID.
 * @param {string} id - Video ID (e.g. "video1")
 * @returns {Promise<Object>} Video object
 */
export async function getVideo(id) {
  const response = await fetch(`${API_BASE_URL}/videos/${id}`);
  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error(`Failed to fetch video: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Send frame to backend for analysis.
 * @param {string} classroomId - Classroom ID (e.g. "8A")
 * @param {string} frameBase64 - Base64 encoded image (data:image/jpeg;base64,...)
 * @returns {Promise<Object>} Analysis result
 */
export async function analyzeFrame(classroomId, frameBase64) {
  const response = await fetch(`${API_BASE_URL}/sentinel/analyze-frame`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      classroom_id: classroomId,
      frame: frameBase64,
    }),
  });
  if (!response.ok) {
    throw new Error(`Failed to analyze frame: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Send audio level to backend for loud noise detection.
 * @param {string} classroomId - Classroom ID (e.g. "8A")
 * @param {number} level - Audio level (0.0 to 1.0)
 * @returns {Promise<Object>} Analysis result
 */
export async function sendAudioLevel(classroomId, level) {
  const response = await fetch(`${API_BASE_URL}/sentinel/audio-level`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      classroom_id: classroomId,
      level: level,
    }),
  });
  if (!response.ok) {
    throw new Error(`Failed to send audio level: ${response.statusText}`);
  }
  return response.json();
}
