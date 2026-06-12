import React, { useState } from 'react';
import styles from '../css/CertificazioniMenu.module.css'; // Assicurati di creare questo file CSS
import Spinner from '../Spinner';
// Importa ReportContext
import { useCertificazioni } from "../../Context/CertificazioniProvider";

const ConfigurazioneSplitFile = ({ setError, setSuccess }) => {

    const [isLoading, setIsLoading] = useState(false);
    const [splitRegion, setSplitRegion] = useState('');
    const [splitPages, setSplitPages] = useState('');
    const [links, setLinks] = useState([]);
    //const [errorMessage, setErrorMessage] = useState('');
    const [file, setFile] = useState(null); // Stato per memorizzare il file selezionato
    const { splitpdf } = useCertificazioni();

    const handleSplitRegionChange = (event) => {
        setSplitRegion(event.target.value);
    };

    const handleSplitPagesChange = (event) => {
        setSplitPages(event.target.value);
    };

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
        formData.append('split_ragion', splitRegion);
        formData.append('split_pages', splitPages);
       
        try {
             // Assumendo che splitpdf restituisca un array di link
             const resultLinks = await splitpdf(formData);
             setLinks(resultLinks); // Memorizza i link nello stato
        } catch (error) {
            console.error('Error splitting PDF', error);
            setError('Si è verificato un errore durante il tentativo di splittare il PDF.');
        }finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <div className={styles.menu}>
                <div>
                    <label htmlFor="fileInput" className={styles.customFileInput}>
                    Select File to Split
                    </label>
                    <input 
                        type='file' 
                        id="fileInput"
                        onChange={handleFileChange} 
                        style={{ display: 'none' }} 
                    />    
                </div>
                <div>
                    <label htmlFor="splitRegion">Choose How to Name the file:</label>
                    <select id="splitRegion" value={splitRegion} onChange={handleSplitRegionChange}>
                        <option value="">Select Option</option>
                        <option value="CF/Piva">CF/Piva</option>
                        <option value="CF">CF</option>
                        <option value="Piva">Piva</option>
                        <option value="Numerato">Numerato</option>
                        <option value="Custom Regex">Custom Regex</option>
                    </select>
                </div>
                <div>
                    <label htmlFor="splitPages">Split Every How Many Pages:</label>
                    <input type="number" id="splitPages" value={splitPages} onChange={handleSplitPagesChange} />
                </div>
                <button onClick={handleSplitFile} disabled={!file || isLoading}>Split File</button>

            </div>
            {isLoading && <Spinner/>}
            <div>
                
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
export default ConfigurazioneSplitFile;