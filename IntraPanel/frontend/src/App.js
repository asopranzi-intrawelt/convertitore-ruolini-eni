import logo from './logo192.png';
import './App.css';
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import Report from './components/Reports/Report';
import FattureSDI from './components/FattureSDI';

function App() {
 return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
      </header>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/report" element={<Report />} />
          <Route path="/fatture-sdi" element={<FattureSDI />} />
          {/* Aggiungi altre rotte qui */}
        </Routes>
      </Router>
    </div>
 );
}

export default App;
