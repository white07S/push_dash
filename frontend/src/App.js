import React from 'react';
import Dashboard from './Dashboard';
import { setSessionContext } from './api/axiosClient';

function App() {
  // Hard-coded session and user IDs as per requirements
  const sessionId = 'session-123456';
  const userId = 'user-demo';

  setSessionContext(sessionId, userId);

  return (
    <Dashboard sessionId={sessionId} userId={userId} />
  );
}

export default App;
