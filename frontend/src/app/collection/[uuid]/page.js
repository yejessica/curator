"use client";

import { useEffect, useState } from 'react';

export default function Collection({ params: paramsPromise }) {
    const [uuid, setUuid] = useState(null);
    const [exhibits, setExhibits] = useState([]);
    const [error, setError] = useState(null);

    // Unwrap `params` using `useEffect`
    useEffect(() => {
        const unwrapParams = async () => {
            const params = await paramsPromise;
            setUuid(params.uuid);
        };

        unwrapParams();
    }, [paramsPromise]);

    // Fetch data only when `uuid` is set
    useEffect(() => {
        if (!uuid) return;

        const fetchData = async () => {
            try {
                const res = await fetch(`http://localhost:5000/api/collection/${uuid}`);
                if (!res.ok) {
                    throw new Error('Failed to fetch data');
                }

                const data = await res.json();
                setExhibits(data.exhibits || []);
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
        <div>
            <h1>Collection Exhibits</h1>
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
    );
}