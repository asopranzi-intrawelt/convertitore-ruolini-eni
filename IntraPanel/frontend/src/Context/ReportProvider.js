import React, { createContext, useContext } from 'react';
import axios from 'axios';

const ReportContext = createContext(null);

const domain = process.env.REACT_APP_REPORT_API || "http://localhost:5000";

const ReportProvider = ({ children }) => {
    const upload = async (data) => {
        const formData = new FormData();
        formData.append('file', data);
        const url = `${domain}/upload`;
        try {
            const response = await axios.post(url, formData);
            return response.data;
        } catch (error) {
            console.log(error);
            throw error;
        };
    };

    const save = async (dataform) => {
        const url = `${domain}/save`;

        try {
            const response = await axios.post(url, dataform);
            return response.data;
        } catch (error) {
            console.log(error);
        };
    };

    const download = async (file) => {
        const url = `${domain}/download/`;

        try {
            window.open(url + file);
        } catch (error) {
            console.log(error);
        };
    };

    return (
        <ReportContext.Provider value={{ upload, save, download }}>
            {children}
        </ReportContext.Provider>
    )
}

export default ReportProvider;

// Funzione per utilizzare il contesto
export const useReport = () => {
    const context = useContext(ReportContext);
    if (!context) {
        throw new Error('useReport must be used within a ReportProvider');
    }
    return context;
};
