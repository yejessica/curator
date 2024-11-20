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
    const [isSaved, setIsSaved] = useState(false);
    const [showCommentModal, setShowCommentModal] = useState(false);
    const [newComment, setNewComment] = useState("");
    const [comments, setComments] = useState([]);

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
                });
                const data = await response.json();
                if (response.ok) {
                    setEmail(data.email);
                    setUsername(data.username);
                } else {
                    setError(data.error);
                    window.location.href = '/login';
                }
            } catch (err) {
                setError('Failed to fetch email.');
            }
        }

        fetchProfile();
    }, []);

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

                // Check if the collection is saved
                const savedRes = await fetch(`http://localhost:5000/api/collection/${uuid}/is-saved`, {
                    credentials: 'include'
                });
                const savedData = await savedRes.json();
                setIsSaved(savedData.is_saved);

                // Fetch comments
                const commentsRes = await fetch(`http://localhost:5000/api/collection/${uuid}/comments`, {
                    credentials: 'include'
                });
                const commentsData = await commentsRes.json();
                setComments(commentsData.comments || []);
            } catch (error) {
                setError(error.message);
            }
        };

        fetchData();
    }, [uuid]);

    const handleLike = async () => {
        try {
            const res = await fetch(`http://localhost:5000/api/collection/${uuid}/like`, {
                method: 'POST',
                credentials: 'include',
            });

            if (!res.ok) {
                throw new Error('Failed to like the collection');
            }

            setLikes((prevLikes) => prevLikes + 1);
        } catch (error) {
            setError(error.message);
        }
    };

    const handleSaveToggle = async () => {
        try {
            const endpoint = isSaved ? 'unsave' : 'save';
            const res = await fetch(`http://localhost:5000/api/collection/${uuid}/${endpoint}`, {
                method: 'POST',
                credentials: 'include',
            });

            if (!res.ok) {
                throw new Error(`Failed to ${isSaved ? 'unsave' : 'save'} the collection`);
            }

            setIsSaved(!isSaved);
        } catch (error) {
            setError(error.message);
        }
    };

    const handleAddComment = async () => {
        if (!newComment.trim()) return;

        try {
            const res = await fetch(`http://localhost:5000/api/collection/${uuid}/comment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ message: newComment }),
            });

            if (!res.ok) {
                throw new Error('Failed to add comment');
            }

            // Refresh comments
            const commentsRes = await fetch(`http://localhost:5000/api/collection/${uuid}/comments`, {
                credentials: 'include'
            });
            const commentsData = await commentsRes.json();
            setComments(commentsData.comments || []);
            setNewComment("");
            setShowCommentModal(false);
        } catch (error) {
            setError(error.message);
        }
    };

    if (error) {
        return <div>Error: {error}</div>;
    }

    if (!uuid) {
        return <div>Loading...</div>;
    }

    return (
        <div className="bg-background font-helvetica text-white min-h-screen w-fill overflow-x-hidden">
            <Navbar username={username} />
            {/* Top info bar */}
            <div className="flex flex-col items-start gap-[30px] self-stretch md:p-[60px_100px] p-[60px_35px]">
                <div className="flex items-center justify-between self-stretch flex-wrap gap-[15px]">
                    {/* Left Col */}
                    <div className="flex flex-col w-[300px] justify-center items-start gap-[18px]">
                        {/* Username/title */}
                        <div className="flex flex-col w-[812px] justify-center items-start gap-[4px]">
                            <h1 className="text-white font-helvetica text-[32px] font-bold">{title}</h1>
                            <h3 className="text-[#BDC1C6] font-helvetica text-xl font-medium">@{collection_username}</h3>
                        </div>
                        {/* Buttons */}
                        <div className="flex items-start gap-[15px] w-full p-0 m-0">
                            <div
                                role="button"
                                className="w-[45px] h-[45px] shrink-0 rounded-[16px] bg-[#086788] flex justify-center items-center hover:bg-[#55b0cf]"
                                onClick={handleLike}
                            >
                                <Image src="/like.svg" width={32} height={32} alt="Like Icon" />
                            </div>
                            <div
                                role="button"
                                className="w-[45px] h-[45px] shrink-0 rounded-[16px] bg-[#086788] flex justify-center items-center hover:bg-[#55b0cf]"
                                onClick={() => setShowCommentModal(true)}
                            >
                                <Image src="/comment.svg" width={32} height={32} alt="Comment Icon" />
                            </div>
                            <div
                                role="button"
                                className={`w-[45px] h-[45px] shrink-0 rounded-[16px] ${
                                    isSaved ? "bg-[#baeeff]" : "bg-[#086788] hover:bg-[#55b0cf]"
                                } flex justify-center items-center`}
                                onClick={handleSaveToggle}
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 32 32"
                                    width="32"
                                    height="32"
                                    fill={isSaved ? "#086788" : "white"} // Dynamically sets the fill color
                                >
                                    <path 
                                        // fill-rule="evenodd" 
                                        // clip-rule="evenodd" 
                                        d="M26 5.99832V27.9983C26 28.797 25.1099 29.2734 24.4453 28.8304L16 23.2013L7.5547 28.8304C6.92179 29.2523 6.08426 28.8403 6.00593 28.1102L6 27.9983V5.99832C6 4.34147 7.34315 2.99832 9 2.99832H23C24.6569 2.99832 26 4.34147 26 5.99832ZM8 26.1303L15.4453 21.1663C15.7812 20.9423 16.2188 20.9423 16.5547 21.1663L24 26.1293V5.99832C24 5.48549 23.614 5.06281 23.1166 5.00505L23 4.99832H9C8.44772 4.99832 8 5.44604 8 5.99832V26.1303Z"
                                    />
                                </svg>
                            </div>

                        </div>
                    </div>
                    {/* Right Col: Views/likes */}
                    <div className="flex justify-center items-center gap-[20px]">
                        <div>
                            <p className="text-[#F9F9F9] text-center font-helvetica text-[15px] font-bold">VIEWS</p>
                            <p className="text-[#F9F9F9] text-center font-helvetica text-[24px] font-light">{views}</p>
                        </div>
                        <div>
                            <p className="text-[#F9F9F9] text-center font-helvetica text-[15px] font-bold">LIKES</p>
                            <p className="text-[#F9F9F9] text-center font-helvetica text-[24px] font-light">{likes}</p>
                        </div>
                    </div>
                </div>
            {/* Display exhibits */}
                <div className="flex flex-wrap items-start self-stretch gap-[20px] break-words">
                {/* <div className="grid grid-cols-3 gap-[20px] items-start self-stretch break-words"> */}
                    {exhibits.map((exhibit, index) => (

                            <div key={index} className="w-full md:w-[48%] lg:w-[31%] xl:w-[32%] p-4 border-2 border-[#cfcfcf1a] rounded-lg shadow-lg block">
                            {exhibit.exhibit_format === "Images" && (
                                <div>
                                    {exhibit.format_specific.images.map((image, index) => (
                                        <img key={index} src={image.url} alt={exhibit.title} className="w-full object-contain" />
                                    ))}
                                </div>
                            )}
                            {exhibit.exhibit_format === "Embeds" && (
                                <div>
                                    {/* <h3>Embeds:</h3> */}
                                    {exhibit.format_specific.embeds.map((embed, index) => (
                                        // <p key={index}>URL: {embed.url}</p>
                                        <div key={index} className='h-fill flex justify-center items-center'>
                                            
                                        <button className="w-[151px] h-[51px] bg-[#086788] hover:bg-[#5099b2] p-[3px_8px] text-[20px] rounded-[25px] font-semibold" key={index} onClick={() => window.open(embed.url, '_blank')}>
                                            Click Here
                                        </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                            {exhibit.exhibit_format === "Texts" && (
                                <div>
                                {exhibit.format_specific.texts.map((textItem, index) => {
                                  // Determine the font class based on textItem.font
                                  let fontClass = '';
                                  let fontFamily = ''; // Variable to hold the inline font family
                              
                                  switch (textItem.font) {
                                    case 'sans':
                                      fontClass = 'font-sans';
                                      fontFamily = 'Arial, sans-serif'; // Define the actual font family
                                      break;
                                    case 'serif':
                                      fontClass = 'font-serif';
                                      fontFamily = 'Times New Roman, serif'; // Define the actual font family
                                      break;
                                    case 'mono':
                                      fontClass = 'font-mono';
                                      fontFamily = 'Courier New, monospace'; // Define the actual font family
                                      break;
                                    default:
                                      fontClass = 'font-sans';
                                      fontFamily = 'Arial, sans-serif'; // Default font family
                                  }
                              
                                  return (
                                    <div key={index} className={fontClass} style={{ fontFamily }}>
                                      <p className='text-[20px]'>{textItem.text}</p>
                                      {/* <p>Font: {textItem.font}</p> */}
                                    </div>
                                  );
                                })}
                              </div>
                              
                              
                              
                            )}
                            {exhibit.exhibit_format === "Videos" && (
                                // <div className="relative w-full h-full pb-[56.25%] flex justify-center items-center">
                                <div>
                                    {/* <h3>Videos:</h3> */}
                                    
                                    {exhibit.format_specific.videos.map((video, index) => (
                                        // <iframe key={index} src={video.url}></iframe>
                                        

                                        video.url.includes("https://www.youtube.com/embed/") ? (
                                            <div key={index} className="relative w-full h-full pb-[56.25%] flex justify-center items-center">
                                            <iframe 
                                                // key={index} 
                                                src={video.url}
                                                className="absolute top-0 left-0 w-full h-full" 
                                            ></iframe>
                                            </div>
                                        ) : (
                                            <div key={index} className='h-fill flex justify-center items-center'>
                                            
                                            <button className="w-[151px] h-[51px] bg-[#086788] hover:bg-[#5099b2] p-[3px_8px] text-[20px] rounded-[25px] font-semibold" key={index} onClick={() => window.open(video.url, '_blank')}>
                                                Watch Here
                                            </button>
                                            </div>
                                        )
                                        
                                
                                    ))}
                                    
                                
                                </div>
                            )}
                            <div className="text-[#c5c9cd] font-helvetica text-[18px] flex flex-wrap justify-between break-words mt-3">
                                <p className="font-bold">{exhibit.title}</p>
                                <p>{new Date(exhibit.created_at).toLocaleDateString()}</p>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-8">
                    <h2 className="text-white font-helvetica text-2xl font-bold mb-4">Comments</h2>
                    {comments.length === 0 ? (
                        <p className="text-[#BDC1C6]">No comments yet. Be the first!</p>
                    ) : (
                        comments.map((comment) => (
                            <div key={comment.comment_id} className="p-4 bg-[#1F2933] rounded-lg mb-4">
                                <p className="text-white font-bold">{comment.username}</p>
                                <p className="text-[#BDC1C6]">{new Date(comment.time).toLocaleString()}</p>
                                <p className="text-white mt-2">{comment.message}</p>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {showCommentModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-[#12171D] p-6 rounded-lg shadow-lg max-w-sm w-full">
                        <h3 className="text-xl font-bold mb-4">Add a Comment</h3>
                        <textarea
                            className="w-full p-2 border border-gray-300 rounded-md mb-4 text-white bg-[#696b6c]"
                            rows="4"
                            placeholder="Write your comment..."
                            value={newComment}
                            onChange={(e) => setNewComment(e.target.value)}
                        />
                        <div className="flex justify-end">
                            <button
                                className="bg-[#8c2439] hover:bg-[#b25366] text-white px-4 py-2 rounded-md mr-2"
                                onClick={() => setShowCommentModal(false)}
                            >
                                Cancel
                            </button>
                            <button
                                className="bg-[#086788] hover:bg-[#5099b2] text-white px-4 py-2 rounded-md"
                                onClick={handleAddComment}
                            >
                                Comment
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}