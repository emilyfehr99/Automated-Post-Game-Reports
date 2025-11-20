import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import TeamDetails from './pages/TeamDetails';
import PlayerDetails from './pages/PlayerDetails';
import Metrics from './pages/Metrics';
import GameDetails from './pages/GameDetails';
import TodaysAction from './pages/TodaysAction';
import PlayoffPredictions from './pages/PlayoffPredictions';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-void">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/team/:id" element={<TeamDetails />} />
          <Route path="/player/:id" element={<PlayerDetails />} />
          <Route path="/metrics" element={<Metrics />} />
          <Route path="/game/:id" element={<GameDetails />} />
          <Route path="/todays-action" element={<TodaysAction />} />
          <Route path="/playoff-race" element={<PlayoffPredictions />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
