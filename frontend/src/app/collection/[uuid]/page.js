"use client";

import { useEffect, useState } from 'react';
import Navbar from '../../../components/Navbar';

export default function Collection({ params: paramsPromise }) {
    const [uuid, setUuid] = useState(null);
    const [exhibits, setExhibits] = useState([]);
    const [title, setTitle] = useState(null);
    const [views, setViews] = useState(null);
    const [likes, setLikes] = useState(null);
    const [error, setError] = useState(null);
    const [username, setUsername] = useState(null);
    const [email, setEmail] = useState(null);
    const [collection_username, setCollectionUsername] = useState(null);

    // Unwrap `params` using `useEffect`
    useEffect(() => {
        const unwrapParams = async () => {
            const params = await paramsPromise;
            setUuid(params.uuid);
        };

        unwrapParams();
    }, [paramsPromise]);

    useEffect(() => {
        async function fetchProfile() {
            try {
                const response = await fetch('http://localhost:5000/api/profile', {
                    credentials: 'include'
                }); // Update to your backend's URL
                const data = await response.json();
                console.log(data);
                if (response.ok) {
                    setEmail(data.email);
                    setUsername(data.username);
                } else {
                    setError(data.error);
                    // Redirect to the login page - probably not logged in
                    window.location.href = '/login';
                }
            } catch (err) {
                setError('Failed to fetch email.');
            }
        }

        fetchProfile();
    }, []);

    // Fetch data and increment views only when `uuid` is set
    useEffect(() => {
        if (!uuid) return;

        const fetchData = async () => {
            try {
                // Increment views
                await fetch(`http://localhost:5000/api/collection/${uuid}/increment-views`, {
                    method: 'POST',
                    credentials: 'include',
                });

                // Fetch collection data
                const res = await fetch(`http://localhost:5000/api/collection/${uuid}`, {
                    credentials: 'include'
                });

                if (!res.ok) {
                    throw new Error('Failed to fetch data');
                }

                const data = await res.json();
                setExhibits(data.exhibits || []);
                setTitle(data.title || 'Untitled Collection');
                setViews(data.views || 0);
                setLikes(data.likes || 0);
                setCollectionUsername(data.collection_username || "");
            } catch (error) {
                setError(error.message);
            }
        };

        fetchData();
    }, [uuid]);

    if (error) {
        return <div>Error: {error}</div>;
    }

    if (!uuid || !exhibits.length) {
        return <div>Loading...</div>;
    }

    return (
        <div className="bg-background font-helvetica text-white min-h-screen">
            {/* <h1>Collection Exhibits</h1> */}

            <Navbar username={username}/>
            <div>
                <div className="flex items-center gap-[252px] self-stretch">
                    <div className="flex flex-col w-[812px] justify-center items-start gap-[25px]">
                        <div className="flex flex-col w-[812px] justify-center items-start gap-2.5">
                            <h1>{title}</h1>
                            <h3>{collection_username}</h3>
                        </div>
                        
                        <div>
                            {/* buttons are here */}
                        </div>
                    </div>
                    <div>

                    </div>
                    
                </div>

                {exhibits.map((exhibit, index) => (
                    <div key={index}>
                        <h2>{exhibit.title}</h2>
                        <p>Created At: {new Date(exhibit.created_at).toLocaleDateString()}</p>
                        <p>Format: {exhibit.exhibit_format}</p>
                        <p>Coordinates: ({exhibit.xcoord}, {exhibit.ycoord})</p>
                        <p>Dimensions: {exhibit.width} x {exhibit.height}</p>
                        <h3>Tags:</h3>
                        <ul>
                            {exhibit.tags.map((tag, index) => (
                                <li key={index}>{tag}</li>
                            ))}
                        </ul>

                        {/* Display format-specific data */}
                        {exhibit.exhibit_format === "Images" && (
                            <div>
                                <h3>Images:</h3>
                                {exhibit.format_specific.images.map((image, index) => (
                                    <p key={index}>URL: {image.url}</p>
                                ))}
                            </div>
                        )}

                        {exhibit.exhibit_format === "Embeds" && (
                            <div>
                                <h3>Embeds:</h3>
                                {exhibit.format_specific.embeds.map((embed, index) => (
                                    <p key={index}>URL: {embed.url}</p>
                                ))}
                            </div>
                        )}

                        {exhibit.exhibit_format === "Texts" && (
                            <div>
                                <h3>Texts:</h3>
                                {exhibit.format_specific.texts.map((textItem, index) => (
                                    <div key={index}>
                                        <p>Text: {textItem.text}</p>
                                        <p>Font: {textItem.font}</p>
                                    </div>
                                ))}
                            </div>
                        )}

                        {exhibit.exhibit_format === "Videos" && (
                            <div>
                                <h3>Videos:</h3>
                                {exhibit.format_specific.videos.map((video, index) => (
                                    <p key={index}>URL: {video.url}</p>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>
            
        </div>
    );
}