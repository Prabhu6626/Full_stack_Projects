import React, { useState } from 'react';
import axios from 'axios';

const CreateEvent = () => {
  const [name, setName] = useState('');
  const [date, setDate] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/events', { name, date, description }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      alert('Event created');
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Event Name" />
      <input type="date" value={date} onChange={(e) => setDate(e.target.value)} placeholder="Event Date" />
      <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Event Description"></textarea>
      <button type="submit">Create Event</button>
    </form>
  );
};

export default CreateEvent;
