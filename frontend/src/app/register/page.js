"use client";

// import { useState } from 'react';
import { useEffect, useState } from 'react';


export default function Register() {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    useEffect(() => {
        async function fetchProfile() {
            try {
                const response = await fetch('http://localhost:5000/api/profile', {
                    credentials: 'include'
                });
                const data = await response.json();
                if (response.ok) {
                    setEmail(data.email);
                    setUsername(data.username);
                    window.location.href = '/dashboard';
                } 
                    // setError(data.error);
                    // window.location.href = '/login';
                    // continue;
                
            } catch (err) {
                setError('Failed to fetch email.');
            }
        }

        fetchProfile();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMessage('');
        setSuccessMessage('');

        try {
            const response = await fetch('http://localhost:5000/api/register', { // Updated URL
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, username, password }),
                credentials: 'include'
            });            
            const data = await response.json();

            if (!response.ok) {
                setErrorMessage(data.error || 'Registration failed.');
                return;
            }

            setSuccessMessage('Registration successful!');

            window.location.href = '/login';

        } catch (error) {
            setErrorMessage('An error occurred. Please try again.');
        }
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <div style={{ maxWidth: '400px', width: '100%', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Register</h2>
                <form onSubmit={handleSubmit}>
                    {/* Display error message if it exists */}
                    {errorMessage && (
                        <p style={{ color: 'red', textAlign: 'center', marginBottom: '15px' }}>{errorMessage}</p>
                    )}
                    <div style={{ marginBottom: '15px' }}>
                        <label htmlFor="email" style={{ display: 'block', marginBottom: '5px' }}>Email</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                            required
                        />
                    </div>
                    <div style={{ marginBottom: '15px' }}>
                        <label htmlFor="username" style={{ display: 'block', marginBottom: '5px' }}>Username</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                            required
                        />
                    </div>
                    <div style={{ marginBottom: '15px' }}>
                        <label htmlFor="password" style={{ display: 'block', marginBottom: '5px' }}>Password</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                            required
                        />
                    </div>
                    <button type="submit" style={{ width: '100%', padding: '10px', backgroundColor: '#0070f3', color: 'white', border: 'none', borderRadius: '4px' }}>
                        Register
                    </button>
                </form>
            </div>
        </div>
    );
}