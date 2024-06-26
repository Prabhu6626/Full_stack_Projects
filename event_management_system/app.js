import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Login from components/Login
import Dashboard from components/Dashboard
import CreateEvent from components/CreateEvent

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/" exact component={Login} />
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/create-event" component={CreateEvent} />
      </Switch>
    </Router>
  );
}

export default App;
