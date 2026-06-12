import React, { useState } from 'react';
import styles from '../css/CertificazioniMenu.module.css'; // Assicurati di creare questo file CSS
import Spinner from '../Spinner';
// Importa ReportContext
import { useCertificazioni } from "../../Context/CertificazioniProvider";

const SearchCFandEmail = ({ setError, setSuccess }) => {

    const [isLoading, setIsLoading] = useState(false);
    const [links, setLinks] = useState([]);
    const [message, setMessage] = useState([]);
    const [notfound, setNotfound] = useState([]);
    const [file, setFile] = useState(null);
    const { searchreplace } = useCertificazioni();

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        const reader = new FileReader();

        reader.onloadend = () => {
            console.log("onloadend");
            // Il risultato è una stringa base64 del file
            const base64File = reader.result;
            // Memorizza la stringa base64 per l'uso successivo
            setFile(base64File);
            //console.log(base64File);
        };
        //console.log(file);
        reader.readAsDataURL(file);
    };

    const handleSplitFile = async () => {
        setIsLoading(true); // Attiva lo spinner
        if (!file) {
            setError('Seleziona un file da splittare.');
            return;
        }
        console.log(file);
        // Rimuovi il prefisso 'data:*/*;base64,' dalla stringa base64
        const fileData = file.split(',')[1];

        let formData = new FormData();
        // Aggiungi la stringa base64 come parte del formData
        formData.append('file', fileData);
       
        try {
             // Assumendo che splitpdf restituisca un array di link
             const resultLinks = await searchreplace(formData);
             setLinks(resultLinks["listlinks"]); // Memorizza i link nello stato
             setMessage(resultLinks["message"]);
             setNotfound(resultLinks["notfound"]);
             setIsLoading(false); // Disattiva lo spinner
        } catch (error) {
            console.error('Error splitting PDF', error);
            setError('Si è verificato un errore durante il tentativo di splittare il PDF.');
            setIsLoading(false); // Disattiva lo spinner
        }
    };

    return (
        <div>
            <div className={styles.menu}>
                <div>
                    <label htmlFor="fileInput" className={styles.customFileInput}>
                    Select File Search CF and Email
                    </label>
                    <input 
                        type='file' 
                        id="fileInput"
                        onChange={handleFileChange} 
                        style={{ display: 'none' }} 
                    />    
                </div>
                
                <button onClick={handleSplitFile} disabled={!file || isLoading}>Split File</button>

            </div>
            {isLoading && <Spinner/>}
            <div>
                <h3>Message</h3>
                {<p>{message}</p>}
                {<p>{notfound}</p>}
                <h3>Links per il download:</h3>
                <ul>
                    {links.map((link, index) => (
                        <li key={index}>
                            <a href={link} target="_blank" rel="noopener noreferrer">{link}</a>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};
export default SearchCFandEmail;