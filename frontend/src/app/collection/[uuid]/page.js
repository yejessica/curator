"use client";

import { useEffect, useState } from 'react';
import Navbar from '../../../components/Navbar';
import Image from 'next/image';

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

    // if (!uuid || !exhibits.length) {
    if (!uuid){
        return <div>Loading...</div>;
    }
    
    return (
        <div className="bg-background font-helvetica text-white min-h-screen">
            {/* <h1>Collection Exhibits</h1> */}

            <Navbar username={username}/>
            
            <div className="flex flex-col items-start gap-[30px] self-stretch md:p-[60px_100px] p-[60px_35px]">
                {/* TOP INFO BAR AREA */}
                <div className="flex items-center gap-[272px] self-stretch flex-wrap">
                    {/* LEFT COL */}
                    <div className="flex flex-col w-[812px] justify-center items-start gap-[18px]">
                        {/* TITLE, USERNAME */}
                        <div className="flex flex-col w-[812px] justify-center items-start gap-[4px]">
                            <h1 className="text-white font-helvetica text-[32px] font-bold">{title}</h1>
                            <h3 className="text-[#BDC1C6] font-helvetica text-xl font-medium">@{collection_username}</h3>
                        </div>
                        {/* BUTTONS */}
                        <div className="flex items-start gap-[15px] w-full p-0 m-0">
                            <div role = "button" className="w-[45px] h-[45px] shrink-0 rounded-[16px] bg-[#086788] flex justify-center items-center">
                                <Image
                                    src="/like.svg"
                                    width={32}
                                    height={32}
                                    alt="Save Icon"
                                />
                            </div>
                            <div role = "button" className="w-[45px] h-[45px] shrink-0 rounded-[16px] bg-[#086788] flex justify-center items-center">
                                <Image
                                    src="/comment.svg"
                                    width={32}
                                    height={32}
                                    alt="Comment Icon"
                                />
                            </div>
                            
                            <div role = "button" className="w-[45px] h-[45px] shrink-0 rounded-[16px] bg-[#086788] flex justify-center items-center">
                                <Image
                                    src="/save.svg"
                                    width={32}
                                    height={32}
                                    alt="Save Icon"
                                />
                            </div>
                          
                        </div>
                    </div>
                    {/* RIGHT COL */}
                    <div className="flex justify-center items-center gap-[20px]">
                        <div>
                            <p className='text-[#F9F9F9] text-center font-helvetica text-[15px] font-bold flex flex-col justify-center shrink-0'>VIEWS</p>
                            <p className="text-[#F9F9F9] text-center font-helvetica text-[24px] font-light flex flex-col justify-center shrink-0">{views}</p>
                        </div>
                        <div>
                            <p className='text-[#F9F9F9] text-center font-helvetica text-[15px] font-bold flex flex-col justify-center shrink-0'>LIKES</p>
                            <p className="text-[#F9F9F9] text-center font-helvetica text-[24px] font-light flex flex-col justify-center shrink-0">{likes}</p>
                        </div>
                    </div>
                    
                </div>

                {/* ALL THE EXHIBITS DISPLAYED */}
                <div className="flex flex-wrap flex-start self-stretch gap-[20px] break-words">
                    
                    {exhibits.map((exhibit, index) => (
                        <div key={index} className="w-full lg:w-[30%] xl:w-[30%] p-4 border rounded-lg shadow-lg">
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
            
        </div>
    );
}