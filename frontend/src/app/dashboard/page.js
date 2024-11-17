'use client';

import { useState, useEffect } from 'react';

export default function Dashboard() {
    const [email, setEmail] = useState(null);
    const [error, setError] = useState(null);
    const [collections, setCollections] = useState([]);

    useEffect(() => {
        async function fetchEmail() {
            try {
                const response = await fetch('http://localhost:5000/api/all-user-collections',{
                    credentials: 'include'
                }); // Update to your backend's URL
                const data = await response.json();
                console.log(data);
                if (response.ok) {
                    setEmail(data.email);
                    setCollections(data.collections)
                } else {
                    setError(data.error);
                }
            } catch (err) {
                setError('Failed to fetch email.');
            }
        }

        fetchEmail();
    }, []);

    if (error) return <p>Error: {error}</p>;
    if (!email) return <p>Loading...</p>;

    return (
        <body className="bg-background">
            {/* <p>Current Email: {email}</p> */}
            <div className="flex flex-col items-start gap-8 flex-1 self-stretch p-[60px_100px]">
                <div className="flex justify-center items-end gap-[349px] self-stretch border-[#ffffff]">
                    <p className="w-[812px] text-white font-helvetica text-4xl font-bold">My Collections</p>

                    <button className="w-[151px] h-[51px] shrink-0 rounded-[20px] bg-[#086788]">New</button>
                </div>
                
                <div className="flex flex-wrap justify-start gap-10 border-[#ffffff]">
                    {collections.map((collection, index) => (
                        <div key={index} role="button" className="flex-grow min-w-[410px] flex-basis-[33.33%] h-[200px] flex-shrink-0 rounded-[20px] border border-[#cfcfcf1a] bg-[#12171D] hover:bg-[#22272E] relative">
                            <p className="w-[328px] h-[35px] text-white font-helvetica text-[24px] font-bold absolute left-[35px] top-[40px]">
                                {collection.title}

                            </p>
                            {/* <div className="left-[83px] top-[129px] mt-2">URL: <a href={collection.url} target="_blank" rel="noopener noreferrer">{collection.url}</a></div> */}
                            <div className="absolute left-[21.5%] top-[129px] text-[#ABABAB] text-center font-helvetica text-xl font-light">
                                <p className='text-[20px]'>{collection.views}</p>
                                <p className='text-[15px] font-semibold'>VIEWS</p>

                            </div>
                            <div className='absolute left-[71.5%] top-[129px] text-[#ABABAB] text-center font-helvetica text-xl font-light'>
                                <p className='text-[20px]'>{collection.likes}</p>
                                <p className='text-[15px] font-semibold'>LIKES</p>
                            </div>

                            <div class="absolute top-[120px] left-1/2 transform -translate-x-1/2 h-[80px] bg-[#cfcfcf1a] w-px"></div>
                            <div class="absolute top-[120px] left-1/2 transform -translate-x-1/2 w-full h-px bg-[#cfcfcf1a]"></div>

                        </div>
                    
                    ))}
                </div>


            </div>
        </body>
        
            
            
     
    );    
}

