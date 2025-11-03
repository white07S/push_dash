import React from 'react';
import Dashboard from './Dashboard';

function App() {
  // Hard-coded session and user IDs as per requirements
  const sessionId = 'session-123456';
  const userId = 'user-demo';

  return (
    <Dashboard sessionId={sessionId} userId={userId} />
  );
}

export default App;
