// ReportMenu.js
import React from 'react';
import styles from '../css/ReportMenu.module.css'; // Assicurati di creare questo file CSS

const ReportMenu = ({ onFileChange, onSave, onDownload, file, enableUpd, enableDown }) => {
 return (
    <div style={{ margin: '10px' }}>
      <label htmlFor="fileInput" className={styles.customFileInput}>
        Scegli File
      </label>
      <input 
        type='file' 
        id="fileInput"
        onChange={onFileChange} 
        style={{ display: 'none' }} 
      />    
      {file && <b style={{ margin: '0 10px' }}>{file.name}</b>}
      <button
        onClick={onSave} disabled={!enableUpd}
        style={{ margin: '10px 0', padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}
      >
        Update Reports
      </button>
      <button
        onClick={onDownload} disabled={!enableDown}
        style={{ margin: '10px 0', padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}
      >
        Download Reports
      </button>
    </div>
 );
};

export default ReportMenu;
