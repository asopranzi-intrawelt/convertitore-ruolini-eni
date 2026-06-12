const domain = "http://localhost:5000/";

export async function uploadReport(req, res) {
    try {
       // Logica per generare il report
       // Ad esempio, recuperare dati dal database, elaborare i dati, ecc.
       const report = await generateUpload();
       res.send(report);
    } catch (error) {
       res.status(500).send('Errore nella generazione del report');
    }
}

export async function saveReport(req, res) {
    try {
       // Logica per generare il report
       // Ad esempio, recuperare dati dal database, elaborare i dati, ecc.
       const report = await generateSave();
       res.send(report);
    } catch (error) {
       res.status(500).send('Errore nella generazione del report');
    }
}

export async function downloadReport(req, res) {
    try {
       // Logica per generare il report
       // Ad esempio, recuperare dati dal database, elaborare i dati, ecc.
       const report = await generateDownload();
       res.send(report);
    } catch (error) {
       res.status(500).send('Errore nella generazione del report');
    }
}

async function generateUpload() {
    const file = req.file;
    // Logica per l'upload del report
    // Ad esempio, invia il file a un servizio esterno o lo salva in un database
    try {
        const response = await axios.post(domain+'/upload', file);
        //res.status(200).json(response.data);
        return response.data;
    } catch (error) {
        res.status(500).json({ error: 'Errore durante l\'upload del report' });
    }
}

async function saveReport() {
    try {
        const response = await axios.post(domain+'/save', file);
        //res.status(200).json(response.data);
        return response.data;
    } catch (error) {
        res.status(500).json({ error: 'Errore durante l\'upload del report' });
    }
}

async function generateDownload() {
    const url = `${domain}/download/`;
    try {
        window.open(url + file);
    } catch (error) {
        console.log(error);
    };
}
