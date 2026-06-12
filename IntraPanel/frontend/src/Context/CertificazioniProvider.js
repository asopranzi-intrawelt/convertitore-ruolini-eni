import React, { createContext, useContext } from 'react';
import axios from 'axios';

const CertificazioniContext = createContext(null);

const domain = process.env.REACT_APP_CERT_API || "http://localhost:4000";

const CertificazioniProvider = ({ children }) => {
    const splitpdf = async (data) => {
        try {
            const url = `${domain}/split-pdf/`;
            const response = await axios.post(url, data, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            console.log(response.data);
            alert('PDF split successfully');
            return downloadFiles(response.data.result);
        } catch (error) {
            console.error('Error splitting PDF', error);
            throw error;
        }
    };


    const downloadFiles = async (filePaths) => {
        const downloadLinks = [];
        for (const filePath of filePaths) {
            try {
                // Assumendo che 'filePath' sia il nome del file senza il percorso
                // e che il server stia servendo i file da '/path/to/your/files/'
                const response = await fetch(`${domain}/download/${filePath}`);
                downloadLinks.push(`${domain}/download/${filePath}`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }else if(response.ok){
                    alert("download avviato");
                }
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                // Suggerisci un nome di file basato sul nome della cartella e sul nome del file
                link.download = `${filePath.split('/').pop()}`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url); // Pulisce l'URL dell'oggetto dopo l'uso
            } catch (error) {
                console.error('Error downloading file', error);
            }
        }
        return downloadLinks;
    };
    
    const searchreplace = async (data) => {
        try {
            const url = `${domain}/searchreplace/`;
            const response = await axios.post(url, data, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            console.log(response.data);
            alert('File completato successfully');
            const resultDict = {
                listlinks: await downloadFiles(response.data.result),
                message: response.data.message,
                notfound: response.data.notfound
            };
            return resultDict;
        } catch (error) {
            console.error('Error splitting PDF', error);
            throw error;
        }
    };

    
    const download = async (file) => {
        const url = `${domain}/download/`;

        try {
            window.open(url + file);
        } catch (error) {
            console.log(error);
        };
    };

    const getConfig = async () => {
        try {
            const url = `${domain}/config`; // Assicurati che 'domain' sia definito correttamente
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
    
            if (response.status != 200) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const configData = await response.json();
            console.log(configData);
            // Qui puoi gestire i dati della configurazione come desideri
            // Ad esempio, potresti volerli visualizzare in un'interfaccia utente
            return configData;
        } catch (error) {
            console.error('Error fetching configuration', error);
            throw error;
        }
    };

    const setConfigEmail = async (data) => {
        try {
            const url = `${domain}/set-config`;
            const response = await axios.post(url, data);

            if (response.status != 200) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            console.log(response.data);
            alert('Configuration saved!');
            return response.data;
        } catch (error) {
            console.error('Error save config email', error);
            throw error;
        }
    };

    const uploadsendfile = async (formData) => {
        console.log("@@@@@");
        console.log(formData);
        try {
            const url = `${domain}/upload-send-file`;
            const response = await axios.post(url, formData);

            if (response.status != 200) {
                throw new Error('Errore durante l\'invio dei file');
            }

            return response.data;
        } catch (error) {
            console.error('Error save config email', error);
            throw error;
        }
    };

    const listFiles = async (typefile) => {
        console.log("@@@@@");
        console.log(`Listing files of type: ${typefile}`);
        try {
            const url = `${domain}/list-files/${typefile}`;
            const response = await axios.get(url);
    
            if (response.status !== 200) {
                throw new Error('Errore durante il recupero dei file');
            }
    
            return response.data;
        } catch (error) {
            console.error('Error fetching files', error);
            throw error;
        }
    };

    const sendEmail = async () => {
        try {
            const url = `${domain}/sendmail`;
            const response = await axios.post(url);
    
            if (response.status !== 200) {
                throw new Error('Errore durante il recupero dei file');
            }
    
            return response.data;
        } catch (error) {
            console.error('Error fetching files', error);
            throw error;
        }
    };

    const progress = async () => {
        try {
            const url = `${domain}/progress`;
            const response = await axios.get(url);
    
            if (response.status !== 200) {
                throw new Error('Errore durante il recupero dei file');
            }
            console.log(response.data);
            return response.data;
        } catch (error) {
            console.error('Error fetching files', error);
            throw error;
        }
    };

    const listUserSend = async () => {
        try {
            const url = `${domain}/users-send`;
            console.log("DDDDD");
            const response = await axios.get(url);
            console.log("CCCCC");
            if (response.status !== 200) {
                throw new Error('Errore durante il recupero dei file');
            }
            console.log(response)
            return response.data;
        } catch (error) {
            console.error('Error fetching files', error);
            throw error;
        }
    };

    return (
        <CertificazioniContext.Provider value={{ splitpdf, download,
         searchreplace, getConfig, setConfigEmail, uploadsendfile, listFiles,
         sendEmail, progress, listUserSend  }}>
            {children}
        </CertificazioniContext.Provider>
    )
}

export default CertificazioniProvider;

// Funzione per utilizzare il contesto
export const useCertificazioni = () => {
    const context = useContext(CertificazioniContext);
    if (!context) {
        throw new Error('useReport must be used within a CertificazioniProvider');
    }
    return context;
};
