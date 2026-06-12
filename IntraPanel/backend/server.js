import express  from 'express';
import reportRouter from './routes/report.js';
const app = express();

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
 console.log(`Server is running on port ${PORT}`);
});


app.use('/report', reportRouter);
