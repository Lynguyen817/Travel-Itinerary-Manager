import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Authentication components
import LoginForm from './components/LoginForm';
import RegistrationForm from './components/RegistrationForm';

// Destination components
import AddDestinationForm from './components/AddDestinationForm';
import DestinationList from './components/DestinationList';
import DestinationDetails from './components/DestinationDetails';

export default function App() {
  const [user, setUser] = useState(null);
  const [destinations, setDestinations] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState(null);

  useEffect(() => {
    // Check if the user is already logged in
    axios.get('/api/check-auth')
      .then(response => {
        setUser(response.data.user);
        fetchDestinations();
      })
      .catch(error => console.error('Authentication check failed', error));
  }, []);

  const fetchDestinations = () => {
    // Fetch user-specific destination data from the backend
    axios.get(`/api/users/${user.id}/destinations`)
      .then(response => setDestinations(response.data))
      .catch(error => console.error('Error fetching destinations', error));
  };

  const handleLogin = (userData) => {
    // Make a request to the backend for user login
    axios.post('/api/login', userData)
      .then(response => {
        setUser(response.data.user);
        fetchDestinations();
      })
      .catch(error => console.error('Login failed', error));
  };

  const handleRegistration = (userData) => {
    // Make a request to the backend for user registration
    axios.post('/api/register', userData)
      .then(response => {
        setUser(response.data.user);
        fetchDestinations();
      })
      .catch(error => console.error('Registration failed', error));
  };

  const handleLogout = () => {
    // Make a request to the backend for user logout
    axios.post('/api/logout')
      .then(() => setUser(null))
      .catch(error => console.error('Logout failed', error));
  };

  const handleAddDestination = (destinationData) => {
    // Make a request to the backend to add a new destination
    axios.post(`/api/users/${user.id}/add_destination`, destinationData)
      .then(() => fetchDestinations())
      .catch(error => console.error('Adding destination failed', error));
  };

  const handleDeleteDestination = (destinationId) => {
    // Make a request to the backend to delete a destination
    axios.post(`/api/users/${user.id}/delete_destination/${destinationId}`)
      .then(() => fetchDestinations())
      .catch(error => console.error('Deleting destination failed', error));
  };

  return (
    <div className="App">
      {!user ? (
        <>
          <LoginForm onLogin={handleLogin} />
          <RegistrationForm onRegister={handleRegistration} />
        </>
      ) : (
        <>
          <button onClick={handleLogout}>Logout</button>

          <AddDestinationForm onAddDestination={handleAddDestination} />

          <DestinationList
            destinations={destinations}
            onSelectDestination={destination => setSelectedDestination(destination)}
            onDeleteDestination={handleDeleteDestination}
          />

          {selectedDestination && (
            <DestinationDetails destination={selectedDestination} />
          )}
        </>
      )}
    </div>
  );
}


