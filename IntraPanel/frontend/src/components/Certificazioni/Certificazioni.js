// Certificazioni.js
import React, { useState } from 'react';
import Layout from '../Layout';
import CertificazioniMenu from './CertificazioniMenu';
import '../css/Certificazioni.css'; // Assicurati di creare questo file CSS
import styles from '../css/DashboardLayout.module.css';
import ListaCertificati from './ListaCertificati';
import ConfigurazioneSplitFile from './ConfigurazioneSplitFile';
import ConfigurazioneEmail from './ConfigurazioneEmail';
import SearchCFandEmail from './SearchCFandEmail';
import InvioEmail from './InvioEmail';
import CaricaFileInvioEmail from './CaricaFileInvioEmail';


const Certificazioni = () => {
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [currentAction, setCurrentAction] = useState('');

    const setError = (error) => {
      setErrorMessage(error);
    };

    const setSuccess = (success) => {
        setSuccessMessage(success);
      };

    const renderContent = () => {
      switch (currentAction) {
          case 'SearchCFandEmail':
              return <SearchCFandEmail 
                        setError={setError}
                        setSuccess={setSuccess}
                    />;
          case 'configurazioneSplitFile':
              return <ConfigurazioneSplitFile
                        setError={setError}
                        setSuccess={setSuccess}
                      />;
          case 'configurazioneEmail':
              return <ConfigurazioneEmail 
                        setError={setError}
                        setSuccess={setSuccess}
                        />;
        case 'CaricaFileInvioEmail':
            return <CaricaFileInvioEmail 
                        setError={setError}
                        setSuccess={setSuccess}
                    />;
        case 'invioEmail':
            return <InvioEmail 
                        setError={setError}
                        setSuccess={setSuccess}
                    />;
          default:
              return <ListaCertificati />;
      }
  };

    return (
        <Layout
            menuComponent={
                <CertificazioniMenu
                    setCurrentAction={setCurrentAction}
                />
            }
            content={
                <div className={styles.mainContent}>
                    {errorMessage && <div className="error-message">{errorMessage}</div>}
                    {successMessage && <div className="success-message">{successMessage}</div>}
                    {renderContent()}
                </div>
            }
        />
    );
};

export default Certificazioni;
