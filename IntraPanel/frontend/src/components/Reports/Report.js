// Report.js

import React, { useState, CSSProperties } from 'react';
import Layout from '../Layout';
import ReportMenu from './ReportMenu';
import '../css/Report.css'; // Assicurati di creare questo file CSS

import Spinner from '../Spinner'; // Adjust the import path as necessary
import styles from '../css/DashboardLayout.module.css'
// Importa ReportContext
import { useReport } from "../../Context/ReportProvider";

const Report = () => {
 // Definisci le funzioni onFileChange, onSave, onDownload, e lo stato del file qui
// Definisci lo stato per il file e le variabili di abilitazione

const [file, setFile] = useState(null);
const [data, setData] = useState([]);
const [enableupd, setEnableUpd] =  useState(false);
const [loading, setLoading] = useState(false);
const [enableDown, setEnableDown] = useState(false);
const [errorMessage, setErrorMessage] = useState('');

const { upload, save, download } = useReport();

const onFileChange = (event) => {
   const file = event.target.files ? event.target.files[0] : null;
   setFile(file);
   if (file) {
       onFileUpload(file);
   }
};


const onFileUpload = async (file) => {
   if (file) { 
      try {
        const data = await upload(file);
        console.log(data);
      if (Array.isArray(data)) {
        setData(data);
        setEnableUpd(true);
      } else {
        console.error("La risposta non è un array:", data);
      }
    } catch (error) {
      setErrorMessage(error.message);
    }

   }
};

const onSave = async () => {
   if (file) {
       setLoading(true);
       const data_resp = await save({ data, filename: file.name });
       setData(data_resp);
       setEnableDown(true);
       setLoading(false);
   }
};

const onDownload = async () => {
  if (file) {
    download(file.name);
  }
};
   // definizione dei tuoi stili
  
   const cellStyle: CSSProperties = {
    border: '0px solid black',
    padding: '10px'
  };

  const cellStyleBorder: CSSProperties = {
    borderBottom: '1px solid #cccccc',
    padding: '10px'
  };
  
  const firstRowStyle: CSSProperties = {
    ...cellStyle,
    backgroundColor: '#ccc',
    color: "#000"
  };
 return (
    <Layout
      menuComponent={
        <ReportMenu
          onFileChange={onFileChange}
          onSave={onSave}
          onDownload={onDownload}
          file={file}
          enableUpd={enableupd}
          enableDown={enableDown}
        />
      }
      content={ <div className={styles.mainContent}>
      <h2>Create Report Eni</h2>
      <h4>List of SO</h4>
      {errorMessage && <div className="error-message">{errorMessage}</div>}
      <table className={styles.table}>

        {loading ? (
          <Spinner />
        ) : (
          Array.isArray(data) && data.slice(2).map((row, index) => (
            <tr key={index}>
              {row.map((cell, i) => <td key={i} style={index === 6 ? firstRowStyle : index > 6 ? cellStyleBorder : cellStyle}>{cell}</td>)}
            </tr>
          ))
        )}
      </table>
      
    </div>}
    />
 );
};

export default Report;
