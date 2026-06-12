// src/components/Home.js
import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
 return (
    <div>
      <h1>Benvenuto nel Pannello Aziendale</h1>
      <div>
        <Link to="/report"><button>Genera Report</button></Link>
        <Link to="/certificazioni"><button>Gestione Certificazioni</button></Link>
        <Link to="/fatture-sdi"><button>Esportazione Fatture SDI</button></Link>
      </div>
    </div>
 );
};

export default Home;
