// Layout.js
import React from 'react';
import { Link } from 'react-router-dom';
import './css/Layout.css';

const Layout = ({ menuComponent, content }) => {
 return (
    <div className="layout">
      <div className="menu">
        {menuComponent}
        <div className="back-button">
          <Link to="/">Torna alla Home</Link>
        </div>
      </div>
      <div className="content">
        {content}
      </div>
    </div>
 );
};

export default Layout;
