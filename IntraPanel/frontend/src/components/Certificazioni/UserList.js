// UserList.js

import React from 'react';

const UserList = ({ users, onClose }) => {
    return (
        <div>
            <h3>Utenti a cui viene inviata la mail:</h3>
            <ul>
                {users.map((user, index) => (
                    <li key={index}>{user}</li>
                ))}
            </ul>
            <button onClick={onClose}>Chiudi</button>
        </div>
    );
};

export default UserList;
