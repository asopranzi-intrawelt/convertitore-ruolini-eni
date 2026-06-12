// report.js
import { Router } from 'express';
import { reportController } from '../controllers/reportController.js'; // Importa la funzione specifica

const router = Router();

router.get('/report/upload', reportController.uploadReport);
router.get('/report/save', reportController.saveReport);
router.get('/report/download', reportController.downloadReport);

export default router;


