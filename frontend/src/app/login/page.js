"use client";

import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    // const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchProfile() {
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/profile`, {
                    credentials: 'include'
                });
                const data = await response.json();

                if (response.ok && data.email && data.username) {
                    setEmail(data.email);
                    setUsername(data.username);
                    window.location.href = '/dashboard'; // Redirect to the dashboard
                } else {
                    setError('Failed to load profile information.');
                }
            } catch (err) {
                setError('Failed to fetch profile.');
            }
        }

        fetchProfile();
    }, []);


    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMessage('');

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
                credentials: 'include'
            });
            const data = await response.json();

            if (!response.ok) {
                setErrorMessage(data.error || 'Login failed.');
                return;
            }
            // login was successful, redirect to dashboard.
            else{
                window.location.href = '/dashboard';
            }
            // Handle successful login (e.g., redirect or set session)
        } catch (error) {
            setErrorMessage('An error occurred. Please try again.');
        }
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <div style={{ maxWidth: '400px', width: '100%', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Login</h2>
                <form onSubmit={handleSubmit}>
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
                        Login
                    </button>
                </form>
                <p style={{ textAlign: 'center', marginTop: '20px' }}>
                    Don&apos;t have an account? <Link href="/register" style={{ color: '#0070f3' }}>Register here</Link>
                </p>

            </div>
        </div>
    );
}