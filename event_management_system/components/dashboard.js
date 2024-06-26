import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  return (
    <div>
      <h1>Dashboard</h1>
      <Link to="/create-event">Create Event</Link>
      <Link to="/events">View Events</Link>
    </div>
  );
};

export default Dashboard;
