import React, { useState, useEffect  } from 'react';
import { useCertificazioni } from "../../Context/CertificazioniProvider";
import Spinner from '../Spinner';
import styles from '../css/common.css'; // Assicurati di creare questo file CSS

const CaricaFileInvioEmail = ({ setError, setSuccess }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [csvFile, setCsvFile] = useState(null);
    const [zipFile, setZipFile] = useState(null);
    const [csvFiles, setCsvFiles] = useState([]);
    const [pdfFiles, setPdfFiles] = useState([]);
    const { uploadsendfile, listFiles } = useCertificazioni();

    // Funzione per richiamare la lista dei file
    const fetchFiles = async () => {
        try {
            const csvFiles = await listFiles('csv');
            const pdfFiles = await listFiles('pdf');
            setCsvFiles(csvFiles.files);
            setSuccess(csvFiles.message)
            setPdfFiles(pdfFiles.files);
            setSuccess(pdfFiles.message)
        } catch (error) {
            setError("Si è verificato un errore durante il recupero dei file.");
        }
    };

    // Chiamata alla funzione fetchFiles dopo il caricamento dei file
    useEffect(() => {
        
        fetchFiles();
        
    }, [csvFile, zipFile]);


    const handleFileChange = (e, setFile) => {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onloadend = () => {
            setFile(reader.result);
          };
          reader.readAsDataURL(file);
        }
     };

     // Funzione per convertire una stringa base64 in un Blob
    function base64ToBlob(base64, mimeType = '') {
        const byteCharacters = atob(base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], {type: mimeType});
    }

    const handleSave = async () => {
        try {
            if (!csvFile || !zipFile) {
                setError("I file CSV e ZIP sono obbligatori.");
                return;
            }

            const confirm = window.confirm("Sei sicuro di voler inviare?");
            if (!confirm) {
                return;
            }

            // Rimuovi il prefisso 'data:*/*;base64,' dalla stringa base64
            const csvFileData = csvFile.split(',')[1];
            const zipFileData = zipFile.split(',')[1];

            // Converti le stringhe base64 in Blob
            const csvFileBlob = base64ToBlob(csvFileData, 'text/csv');
            const zipFileBlob = base64ToBlob(zipFileData, 'application/zip');
            console.log(csvFileBlob)
            // Crea un oggetto FormData per caricare i file
            let formData = new FormData();
            formData.append('csvFile', csvFileBlob); // Aggiungi il file CSV
            formData.append('zipFile', zipFileBlob); // Aggiungi il file ZIP
            console.log(formData);
            const resultConfig = await uploadsendfile(formData);
            setSuccess(resultConfig.message);
            setIsLoading(true);
        
        } catch (error) {
            setError("Si è verificato un errore durante l'invio.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <h2>Invio Email</h2>
            {isLoading && <Spinner/>}
            {(
                <div className="form-container">
                    <label>Carica file csv con gli indirizzi</label>
                    <input type="file" onChange={(e) => handleFileChange(e, setCsvFile)} />
                    <label>Carica file zip con i pdf dei cud Firmati.</label>
                    <input type="file" onChange={(e) => handleFileChange(e, setZipFile)} />
                    <button onClick={handleSave}>Carica file</button>
                </div>
            )}
            <div>
                <h3>File CSV caricati:</h3>
                <ul>
                    {csvFiles.map((file, index) => (
                        <li key={index}>{file}</li>
                    ))}
                </ul>
                <h3>File PDF caricati:</h3>
                <ul>
                    {pdfFiles.map((file, index) => (
                        <li key={index}>{file}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default CaricaFileInvioEmail;
