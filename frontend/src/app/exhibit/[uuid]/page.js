"use client";

import { useEffect, useState } from 'react';

export default function Exhibit({ params }) {
    const { uuid } = params;
    const [exhibit, setExhibit] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch(`http://localhost:5000/api/exhibit/${uuid}`);
                if (!res.ok) {
                    throw new Error('Failed to fetch data');
                }

                const data = await res.json();
                setExhibit(data.exhibit || null);
            } catch (error) {
                setError(error.message);
            }
        };

        fetchData();
    }, [uuid]);

    if (error) {
        return <div>Error: {error}</div>;
    }

    if (!exhibit) {
        return <div>Loading...</div>;
    }

    const { format_specific } = exhibit;

    return (
        <div>
            <h1>Exhibit: {exhibit.title}</h1>
            <p>Created At: {new Date(exhibit.created_at).toLocaleDateString()}</p>
            <p>Format: {exhibit.exhibit_format}</p>
            <p>Coordinates: ({exhibit.xcoord}, {exhibit.ycoord})</p>
            <p>Dimensions: {exhibit.width} x {exhibit.height}</p>
            <p>Collection: {exhibit.collection_name}</p>
            <h3>Tags:</h3>
            <ul>
                {exhibit.tags.map((tag, index) => (
                    <li key={index}>{tag}</li>
                ))}
            </ul>

            {/* Display format-specific data */}
            {exhibit.exhibit_format === "images" && (
                <div>
                    <h3>Images:</h3>
                    {format_specific.images.map((image, index) => (
                        <p key={index}>Directory: {image.directory}</p>
                    ))}
                </div>
            )}

            {exhibit.exhibit_format === "embeds" && (
                <div>
                    <h3>Embeds:</h3>
                    {format_specific.embeds.map((embed, index) => (
                        <p key={index}>Directory: {embed.directory}</p>
                    ))}
                </div>
            )}

            {exhibit.exhibit_format === "texts" && (
                <div>
                    <h3>Texts:</h3>
                    {format_specific.texts.map((textItem, index) => (
                        <div key={index}>
                            <p>Text: {textItem.text}</p>
                            <p>Font: {textItem.font}</p>
                        </div>
                    ))}
                </div>
            )}

            {exhibit.exhibit_format === "videos" && (
                <div>
                    <h3>Videos:</h3>
                    {format_specific.videos.map((video, index) => (
                        <p key={index}>Directory: {video.directory}</p>
                    ))}
                </div>
            )}
        </div>
    );
}