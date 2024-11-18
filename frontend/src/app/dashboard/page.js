'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation'; // Import useRouter

export default function Dashboard() {
    const [email, setEmail] = useState(null);
    const [error, setError] = useState(null);
    const [collections, setCollections] = useState([]);
    const [username, setUsername] = useState(null);
    const router = useRouter(); // Initialize useRouter

    useEffect(() => {
        async function fetchEmail() {
            try {
                const response = await fetch('http://localhost:5000/api/all-user-collections', {
                    credentials: 'include'
                }); // Update to your backend's URL
                const data = await response.json();
                console.log(data);
                if (response.ok) {
                    setEmail(data.email);
                    setUsername(data.username);
                    setCollections(data.collections);
                } else {
                    setError(data.error);
                    // Redirect to the login page - probably not logged in
                    window.location.href = '/login';
                }
            } catch (err) {
                setError('Failed to fetch email.');
            }
        }

        fetchEmail();
    }, []);

    // ERROR MESSAGE
    if (error) return <p>Error: {error}</p>;

    // LOADING SCREEN!!
    if (!email) return (
        <div className="min-h-screen flex justify-center items-center bg-background">
            <div className='w-64 h-32 text-center flex items-center justify-center text-white'>
                <p className="font-helvetica text-[32px]">Loading...</p>
            </div>
        </div>
    );

    // ACTUAL DASHBOARD
    return (
        <div className="bg-background font-helvetica text-white min-h-screen">
            {/* MENU BAR */}
            <div className="bg-gradient-to-r from-[#12171D] via-[rgba(7,68,89,0.2)] to-[rgba(0,0,0,0.2)] border-[#12171D] shadow-md flex items-start p-[20px_100px] justify-end space-x-[80px]">
                <div className="flex items-start space-x-[5px]">
                    <Image
                        src="/profile-icon.svg"
                        width={28}
                        height={28}
                        alt="Profile Icon"
                    />
                    <p className="text-white font-helvetica text-[18px] font-bold">{username}</p>
                </div>
                
                <div role="button"
                    className="flex items-start space-x-[5px]"
                    onClick={async () => {
                        try {
                            const response = await fetch('http://localhost:5000/api/logout', {
                                method: 'POST',
                                credentials: 'include',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                            });

                            if (response.ok) {
                                // Handle successful logout
                                console.log('Logged out successfully');
                                // Redirect to login or home page
                                window.location.href = '/login';
                            } else {
                                console.error('Logout failed');
                            }
                        } catch (error) {
                            console.error('Error logging out:', error);
                        }
                    }}>
                    <Image
                        src="/logout-icon.svg"
                        width={28}
                        height={28}
                        alt="Logout Icon"
                    />
                    <p className="text-[#55D3FF] font-helvetica text-[18px] font-bold hover:text-[#9fe5ff]">Logout</p>
                </div>
            </div>

            <div className="flex flex-col items-start gap-8 flex-1 self-stretch md:p-[60px_100px] p-[60px_35px]">
                <div className="flex justify-between border-[#ffffff] w-[100%]">
                    <p className="w-[812px] text-white font-helvetica text-4xl font-bold">My Collections</p>
                    <button
                        className="w-[151px] h-[51px] shrink-0 rounded-[25px] bg-[#086788] text-white text-[20px] font-semibold hover:bg-[#31819c]"
                        onClick={() => router.push('/create')} // Navigate to /create on click
                    >
                        New
                    </button>
                </div>

                <div className="flex flex-wrap justify-start gap-10 border-[#ffffff]">
                    {collections.map((collection, index) => (
                        <div key={index} role="button" className="flex-grow min-w-[410px] flex-basis-[33.33%] h-[200px] flex-shrink-0 rounded-[20px] border border-[#cfcfcf1a] bg-[#12171D] hover:bg-[#22272E] relative">
                            <p className="w-[328px] h-[35px] text-white font-helvetica text-[24px] font-bold absolute left-[35px] top-[40px]">
                                {collection.title}
                            </p>
                            <div className="absolute left-[21.5%] top-[129px] text-[#ABABAB] text-center font-helvetica text-xl font-light">
                                <p className='text-[20px]'>{collection.views}</p>
                                <p className='text-[15px] font-semibold'>VIEWS</p>
                            </div>
                            <div className='absolute left-[71.5%] top-[129px] text-[#ABABAB] text-center font-helvetica text-xl font-light'>
                                <p className='text-[20px]'>{collection.likes}</p>
                                <p className='text-[15px] font-semibold'>LIKES</p>
                            </div>

                            <div className="absolute top-[120px] left-1/2 transform -translate-x-1/2 h-[80px] bg-[#cfcfcf1a] w-px"></div>
                            <div className="absolute top-[120px] left-1/2 transform -translate-x-1/2 w-full h-px bg-[#cfcfcf1a]"></div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}