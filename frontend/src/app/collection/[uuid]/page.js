'use client';

import { use } from 'react';
import { useEffect, useState } from 'react';

export default function Collection({ params }) {
    const { uuid } = use(params);
    const [exhibits, setExhibits] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
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
                    <p>Owner: {exhibit.username}</p>
                </div>
            ))}
        </div>
    );
}