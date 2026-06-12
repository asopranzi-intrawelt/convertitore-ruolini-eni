import React, { useEffect, useState } from 'react';
import { useCertificazioni } from "../../Context/CertificazioniProvider";
import UserList from './UserList';

const InvioEmail = ({setError, setSuccess}) => {
    const [isLoading, setIsLoading] = useState(false);
    const [progresssend, setProgressSend] = useState({});
    const [isSendingEmail, setIsSendingEmail] = useState(false);
    const [isEmailSent, setIsEmailSent] = useState(false);
    const [showUserList, setShowUserList] = useState(false);
    const [users, setUsers] = useState([]); // Lista degli utenti a cui viene inviata la mail
    const { sendEmail, progress, listUserSend } = useCertificazioni(); // Assicurati che sendEmail sia definito nel tuo context

    useEffect(() => {
        setSuccess(""); // Attiva lo spinner
        setError("")
        let intervalId;
        const fetchData = async () => {
            try {
                setSuccess(""); // Attiva lo spinner
                setError("");
                const users = await listUserSend(); // Assicurati che listUserSend sia definita e accessibile
                // Dopo il successo, puoi impostare lo stato di successo qui
                setUsers(users);
                setShowUserList(true);
                setSuccess("Operazione completata con successo");
            } catch (err) {
                // Gestisci eventuali errori qui
                setError("Si è verificato un errore durante l'operazione");
            }
        };

        fetchData();
        
        if (isSendingEmail && !isEmailSent) {
            const fetchProgress = async () => {
                try {
                    const response = await progress();
                    setProgressSend(response);
                } catch (error) {
                    console.error('Error fetching progress:', error);
                }
            };

            // Chiama l'endpoint ogni 5 secondi
            const intervalId = setInterval(fetchProgress, 5000);
        }
        // Pulisce l'intervallo quando il componente viene smontato
        return () => clearInterval(intervalId);
    }, [isSendingEmail, isEmailSent]);

    const handleSendEmail = async () => {
        setIsLoading(true); // Attiva lo spinner
        try {
            setIsSendingEmail(true);
             // Assumendo che splitpdf restituisca un array di link
             const result = await sendEmail();
             setIsEmailSent(true);
             setSuccess(result)
             
        } catch (error) {
            console.error('Error splitting PDF', error);
            setError('Si è verificato un errore durante il tentativo di splittare il PDF.');
        }finally {
            setIsEmailSent(true);
            setIsLoading(false);
        }
    };

    const handleCloseUserList = () => {
        setShowUserList(!showUserList);
    };

    return (
        <div>
            <button onClick={handleSendEmail}>Invia Email</button>
            <h2>Stato di avanzamento:</h2>
            <ul>
                {Object.entries(progresssend).map(([email, status]) => (
                    <li key={email}>{email}: {status}</li>
                ))}
            </ul>
            {showUserList && <UserList users={users} onClose={handleCloseUserList} />}
        </div>
    );
};

export default InvioEmail;