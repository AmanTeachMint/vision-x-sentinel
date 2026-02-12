import React, { useState, useEffect, useCallback } from 'react';
import ClassCard from './ClassCard';
import { getClassrooms, getVideos, analyzeFrame } from '../api/client';
import { useAlerts } from '../hooks/useAlerts';

function Dashboard({ searchQuery = '', routeClassId = null }) {
  const [classrooms, setClassrooms] = useState([]);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { recentAlertClassroomIds } = useAlerts();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [classroomsData, videosData] = await Promise.all([
        getClassrooms(),
        getVideos(),
      ]);
      setClassrooms(classroomsData);
      setVideos(videosData);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFrameCapture = useCallback(async (classroomId, frameBase64) => {
    const result = await analyzeFrame(classroomId, frameBase64);
    if (result?.current_status) {
      setClassrooms((prev) =>
        prev.map((c) => (c.id === classroomId ? { ...c, current_status: result.current_status } : c))
      );
    }
  }, []);

  // Map classroom_id -> video URL (videos have classroom_id; first video per classroom wins)
  const classroomIdToVideoUrl = {};
  videos.forEach((video) => {
    if (video.classroom_id && !classroomIdToVideoUrl[video.classroom_id]) {
      classroomIdToVideoUrl[video.classroom_id] = video.url;
    }
  });

  // Filter classrooms by search query
  let filteredClassrooms = searchQuery
    ? classrooms.filter(c =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.id.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : classrooms;

  if (routeClassId) {
    filteredClassrooms = classrooms.filter(
      (c) => c.id.toLowerCase() === routeClassId.toLowerCase()
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">Loading classrooms...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-red-400">Error: {error}</div>
      </div>
    );
  }

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {filteredClassrooms.map((classroom) => {
          // Get video URL from videos that have this classroom_id
          const videoUrl = classroomIdToVideoUrl[classroom.id] || null;
          return (
            <ClassCard
              key={classroom.id}
              classroom={classroom}
              videoUrl={videoUrl}
              onFrameCapture={handleFrameCapture}
              hasNewAlert={recentAlertClassroomIds.includes(classroom.id)}
            />
          );
        })}
      </div>
      {filteredClassrooms.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          No classrooms found matching "{searchQuery}"
        </div>
      )}

    </div>
  );
}

export default Dashboard;
