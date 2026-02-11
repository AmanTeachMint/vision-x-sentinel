import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import { getClassrooms } from './api/client';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [classrooms, setClassrooms] = useState([]);

  useEffect(() => {
    loadClassrooms();
  }, []);

  const loadClassrooms = async () => {
    try {
      const data = await getClassrooms();
      setClassrooms(data);
    } catch (err) {
      console.error('Failed to load classrooms:', err);
    }
  };

  const activeCount = classrooms.filter(c => c.current_status === 'active').length;
  const inactiveCount = classrooms.filter(c => c.current_status === 'inactive').length;

  return (
    <Layout
      activeCount={activeCount}
      inactiveCount={inactiveCount}
      onRefresh={loadClassrooms}
      onSearchChange={setSearchQuery}
      searchValue={searchQuery}
    >
      <Dashboard searchQuery={searchQuery} />
    </Layout>
  );
}

export default App;
