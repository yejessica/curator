"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '../../components/Navbar';

export default function Dashboard() {
    const [email, setEmail] = useState(null);
    const [error, setError] = useState(null);
    const [collections, setCollections] = useState([]);
    const [savedCollections, setSavedCollections] = useState([]);
    const [username, setUsername] = useState(null);
    const router = useRouter();

    useEffect(() => {
        async function fetchEmail() {
            try {
                const response = await fetch('http://localhost:5000/api/all-user-collections', {
                    credentials: 'include'
                });
                const data = await response.json();
                if (response.ok) {
                    setEmail(data.email);
                    setUsername(data.username);
                    setCollections(data.collections);
                } else {
                    setError(data.error);
                    window.location.href = '/login';
                }
            } catch (err) {
                setError('Failed to fetch email.');
            }
        }

        async function fetchSavedCollections() {
            try {
                const response = await fetch('http://localhost:5000/api/saved-collections', {
                    credentials: 'include'
                });
                const data = await response.json();
                if (response.ok) {
                    setSavedCollections(data.saved_collections);
                } else {
                    setError(data.error);
                }
            } catch (err) {
                setError('Failed to fetch saved collections.');
            }
        }

        fetchEmail();
        fetchSavedCollections();
    }, []);

    if (error) return <p>Error: {error}</p>;

    if (!email) return (
        <div className="min-h-screen flex justify-center items-center bg-background">
            <div className="w-64 h-32 text-center flex items-center justify-center text-white">
                <p className="font-helvetica text-[32px]">Loading...</p>
            </div>
        </div>
    );

    return (
        <div className="bg-background font-helvetica text-white min-h-screen">
            <Navbar username={username} />

            <div className="flex flex-col items-start gap-8 flex-1 self-stretch md:p-[60px_100px] p-[60px_35px]">
                <div className="flex justify-between border-[#ffffff] w-[100%]">
                    <p className="w-[812px] text-white font-helvetica text-4xl font-bold">My Collections</p>
                    <button
                        className="w-[151px] h-[51px] shrink-0 rounded-[25px] bg-[#086788] text-white text-[20px] font-semibold hover:bg-[#31819c]"
                        onClick={() => router.push('/create')}
                    >
                        New
                    </button>
                </div>

                <div className="flex flex-wrap justify-start gap-10 border-[#ffffff]">
                    {collections.map((collection, index) => (
                        <div
                            key={index}
                            role="button"
                            className="flex-grow min-w-[410px] flex-basis-[33.33%] h-[200px] flex-shrink-0 rounded-[20px] border border-[#cfcfcf1a] bg-[#12171D] hover:bg-[#22272E] relative"
                            onClick={() => router.push(`/collection/${collection.url}`)}
                        >
                            <p className="w-[328px] h-[35px] text-white font-helvetica text-[24px] font-bold absolute left-[35px] top-[40px]">
                                {collection.title}
                            </p>
                            <div className="absolute left-[21.5%] top-[129px] text-[#ABABAB] text-center font-helvetica text-xl font-light">
                                <p className="text-[20px]">{collection.views}</p>
                                <p className="text-[15px] font-semibold">VIEWS</p>
                            </div>
                            <div className="absolute left-[71.5%] top-[129px] text-[#ABABAB] text-center font-helvetica text-xl font-light">
                                <p className="text-[20px]">{collection.likes}</p>
                                <p className="text-[15px] font-semibold">LIKES</p>
                            </div>

                            <div className="absolute top-[120px] left-1/2 transform -translate-x-1/2 h-[80px] bg-[#cfcfcf1a] w-px"></div>
                            <div className="absolute top-[120px] left-1/2 transform -translate-x-1/2 w-full h-px bg-[#cfcfcf1a]"></div>
                        </div>
                    ))}
                </div>

                <p className="w-[812px] text-white font-helvetica text-4xl font-bold mt-8">Saved Collections</p>
                <div className="flex flex-wrap justify-start gap-10 border-[#ffffff]">
                    {savedCollections.map((collection, index) => (
                        <div
                            key={index}
                            role="button"
                            className="flex-grow min-w-[410px] flex-basis-[33.33%] h-[200px] flex-shrink-0 rounded-[20px] border border-[#cfcfcf1a] bg-[#12171D] hover:bg-[#22272E] relative"
                            onClick={() => router.push(`/collection/${collection.url}`)}
                        >
                            <p className="w-[328px] h-[35px] text-white font-helvetica text-[24px] font-bold absolute left-[35px] top-[40px]">
                                {collection.title}
                            </p>
                            <div className="absolute left-[21.5%] top-[129px] text-[#ABABAB] text-center font-helvetica text-xl font-light">
                                <p className="text-[20px]">{collection.views}</p>
                                <p className="text-[15px] font-semibold">VIEWS</p>
                            </div>
                            <div className="absolute left-[71.5%] top-[129px] text-[#ABABAB] text-center font-helvetica text-xl font-light">
                                <p className="text-[20px]">{collection.likes}</p>
                                <p className="text-[15px] font-semibold">LIKES</p>
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