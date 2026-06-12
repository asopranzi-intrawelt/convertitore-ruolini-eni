// CertificazioniMenu.js
import React from 'react';
import styles from '../css/CertificazioniMenu.module.css'; // Assicurati di creare questo file CSS

const CertificazioniMenu = ({ setCurrentAction }) => {

    const handleActionChange = (action) => {
      setCurrentAction(action);
    };

    return (
        <div className={styles.menu}>
            {/* Aggiungi i pulsanti per cambiare l'azione */}
            <button onClick={() => handleActionChange('listaCertificati')}>Lista Certificati</button>
            <button onClick={() => handleActionChange('configurazioneSplitFile')}>Configurazione Split File</button>
            <button onClick={() => handleActionChange('SearchCFandEmail')}>Search CF and Email</button>
            <button onClick={() => handleActionChange('configurazioneEmail')}>Configurazione Email</button>
            <button onClick={() => handleActionChange('CaricaFileInvioEmail')}>Carica file Invio Email</button>
            <button onClick={() => handleActionChange('invioEmail')}>Invio Email</button>
            {/* Il resto del codice rimane invariato */}
        </div>
    );
};

export default CertificazioniMenu;
