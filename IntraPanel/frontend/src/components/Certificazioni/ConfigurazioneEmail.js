
import { useCertificazioni } from "../../Context/CertificazioniProvider";
import React, { useState } from 'react';
import Spinner from '../Spinner';
import styles from '../css/common.css'; // Assicurati di creare questo file CSS

const ConfigurazioneEmail = ({ setError, setSuccess }) => {

    const [isLoading, setIsLoading] = useState(false);
    const { getConfig, setConfigEmail } = useCertificazioni();

    const [config, setConfig] = useState({
        smtp_ssl_host: '',
        smtp_ssl_port: '',
        email_user: '',
        subject: '',
        messaggio_html: ''
    });

    const handleConfigEmail = async () => {
        setIsLoading(true); // Attiva lo spinner
        try {
             // Assumendo che splitpdf restituisca un array di link
             const resultConfig = await getConfig();
             console.log(resultConfig);
             setConfig(resultConfig);
             setIsLoading(false); // Disattiva lo spinner
        } catch (error) {
            console.error('Error splitting PDF', error);
            setError('Si è verificato un errore durante il tentativo di splittare il PDF.');
            setIsLoading(false); // Disattiva lo spinner
        }
    };

    const handleInputChange = (event) => {
        const { name, value } = event.target;
        setConfig(prevConfig => ({
            ...prevConfig,
            [name]: value
        }));
    };

    const isConfigComplete = () => {
        return config.smtp_ssl_host && config.smtp_ssl_port && config.email_user && config.subject;
    };

    const handleSave = async () => {
        setIsLoading(true); // Attiva lo spinner
        try {
             // Assumendo che splitpdf restituisca un array di link
             const resultConfig = await setConfigEmail(config);
             console.log(resultConfig);
             setConfig(resultConfig);
             // Verifica che la risposta contenga la chiave 'result'
            if (resultConfig.result) {
                setConfig(resultConfig.result);
            }
            if (resultConfig.message) {
                setSuccess(resultConfig.message)
            }
             setIsLoading(false); // Disattiva lo spinner
        } catch (error) {
            console.error('Error nel salvataggio email', error);
            setError('Si è verificato un errore durante il tentativo di splittare il PDF.');
            setIsLoading(false); // Disattiva lo spinner
        }
    };


    return (
        <div>
            <h2>Configurazione Email</h2>
            <button onClick={handleConfigEmail} disabled={isLoading}>Carica Configurazione</button>
            {isLoading && <Spinner/>}
            {isConfigComplete() && (
            <div className="form-container">
                <label>
                    Host SMTP SSL:
                    <input type="text" name="smtp_ssl_host" value={config.smtp_ssl_host} onChange={handleInputChange} />
                </label>
                <br />
                <label>
                    Porta SMTP SSL:
                    <input type="text" name="smtp_ssl_port" value={config.smtp_ssl_port} onChange={handleInputChange} />
                </label>
                <br />
                <label>
                    Utente Email:
                    <input type="text" name="email_user" value={config.email_user} onChange={handleInputChange} />
                </label>
                <label>
                    Oggetto:
                    <input type="text" name="subject" value={config.subject} onChange={handleInputChange} />
                </label>
                <label>
                    Messaggio:
                    <textarea type="text" name="messaggio_html" value={config.messaggio_html} onChange={handleInputChange} />
                </label>
                <label>
                    messaggio_html
                    <div dangerouslySetInnerHTML={{ __html: config.messaggio_html }} />
                </label>
                <button onClick={handleSave}>Salva Configurazione</button>
            </div>
             )}
        </div>
    );
};

export default ConfigurazioneEmail;