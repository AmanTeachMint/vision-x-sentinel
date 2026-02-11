import React, { useState, useEffect } from 'react';
import ClassCard from './ClassCard';
import { getClassrooms, getVideos, analyzeFrame } from '../api/client';
import { useAlerts } from '../hooks/useAlerts';

function Dashboard({ searchQuery = '' }) {
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

  const handleFrameCapture = async (classroomId, frameBase64) => {
    try {
      await analyzeFrame(classroomId, frameBase64);
    } catch (err) {
      console.error(`Analyze frame for ${classroomId}:`, err.message);
    }
  };

  // Create a map of video_id -> video URL for quick lookup
  const videoMap = videos.reduce((acc, video) => {
    acc[video.id] = video.url;
    return acc;
  }, {});

  // Filter classrooms by search query
  const filteredClassrooms = searchQuery
    ? classrooms.filter(c => 
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.id.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : classrooms;

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
          // Get video URL from videoMap using classroom.video_id
          const videoUrl = classroom.video_id ? videoMap[classroom.video_id] : null;
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
