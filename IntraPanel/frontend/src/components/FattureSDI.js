import React from 'react';
import Layout from './Layout'; // Assicurati che il percorso sia corretto

const FattureSDI = () => {
  const menu = (
    <div>
      <button>Link 1</button>
      <button>Link 2</button>
      <button>Link 3</button>
    </div>
 );
 const content = (
  <div>
     <h1>FattureSDI</h1>
    <p>Contenuto delle FattureSDI</p>
  </div>
);
return <Layout menu={menu} content={content} />;
};

export default FattureSDI;

