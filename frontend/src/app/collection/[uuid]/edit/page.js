"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";

export default function EditCollection() {
    const router = useRouter();
    const { uuid } = useParams();

    const [collectionName, setCollectionName] = useState("");
    const [exhibits, setExhibits] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Fetch collection data
        const fetchCollection = async () => {
            try {
                const res = await fetch(`http://localhost:5000/api/collection/${uuid}/edit`, {
                    credentials: "include"
                });

                if (res.status === 401) {
                    // Redirect to login if not authenticated
                    router.push("/login");
                } else if (res.status === 403) {
                    // Redirect to dashboard if not the owner
                    router.push("/dashboard");
                } else if (!res.ok) {
                    throw new Error("Failed to fetch collection data");
                } else {
                    const data = await res.json();
                    setCollectionName(data.title);
                    setExhibits(data.exhibits);
                    setLoading(false);
                }
            } catch (error) {
                setError(error.message);
            }
        };

        fetchCollection();
    }, [uuid, router]);

    const handleExhibitChange = (index, field, value) => {
        const newExhibits = [...exhibits];
        newExhibits[index][field] = value;
        setExhibits(newExhibits);
    };

    const handleSubmit = async () => {
        try {
            const res = await fetch(`http://localhost:5000/api/collection/${uuid}/edit`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ title: collectionName, exhibits })
            });

            if (!res.ok) {
                throw new Error("Failed to update collection");
            }

            // Redirect to the updated collection view
            router.push(`/collection/${uuid}`);
        } catch (error) {
            setError(error.message);
        }
    };

    if (loading) return <p>Loading...</p>;

    return (
        <div className="max-w-4xl mx-auto p-6 bg-gray-100 rounded-lg shadow-md">
            <h1 className="text-2xl font-bold mb-4">Edit Collection</h1>
            <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Collection Name:</label>
                <input
                    type="text"
                    className="w-full p-2 border border-gray-300 rounded-md"
                    value={collectionName}
                    onChange={(e) => setCollectionName(e.target.value)}
                />
            </div>

            <h2 className="text-xl font-semibold mb-3">Exhibits</h2>
            {exhibits.map((exhibit, index) => (
                <div key={index} className="mb-4 p-4 bg-white border border-gray-200 rounded-md shadow-sm">
                    <input
                        type="text"
                        placeholder="Title"
                        className="w-full p-2 border border-gray-300 rounded-md mb-2"
                        value={exhibit.title}
                        onChange={(e) => handleExhibitChange(index, "title", e.target.value)}
                    />

                    <select
                        className="w-full p-2 border border-gray-300 rounded-md mb-2"
                        value={exhibit.exhibit_format}
                        onChange={(e) => handleExhibitChange(index, "exhibit_format", e.target.value)}
                    >
                        <option value="">Select Format</option>
                        <option value="Images">Images</option>
                        <option value="Videos">Videos</option>
                        <option value="Embeds">Embeds</option>
                        <option value="Texts">Texts</option>
                    </select>

                    {/* Show URL input for relevant formats */}
                    {(exhibit.exhibit_format === "Images" || exhibit.exhibit_format === "Videos" || exhibit.exhibit_format === "Embeds") && (
                        <input
                            type="text"
                            placeholder="URL"
                            className="w-full p-2 border border-gray-300 rounded-md"
                            value={exhibit.url}
                            onChange={(e) => handleExhibitChange(index, "url", e.target.value)}
                        />
                    )}

                    {/* Show text and font inputs for text exhibits */}
                    {exhibit.exhibit_format === "Texts" && (
                        <>
                            <input
                                type="text"
                                placeholder="Text"
                                className="w-full p-2 border border-gray-300 rounded-md mb-2"
                                value={exhibit.text}
                                onChange={(e) => handleExhibitChange(index, "text", e.target.value)}
                            />
                            <select
                                className="w-full p-2 border border-gray-300 rounded-md"
                                value={exhibit.font}
                                onChange={(e) => handleExhibitChange(index, "font", e.target.value)}
                            >
                                <option value="">Select Font</option>
                                <option value="sans">Sans</option>
                                <option value="serif">Serif</option>
                                <option value="mono">Mono</option>
                            </select>
                        </>
                    )}
                </div>
            ))}

            {error && <p className="text-red-500 mt-4">{error}</p>}

            <button
                className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 mt-4"
                onClick={handleSubmit}
            >
                Save Changes
            </button>
        </div>
    );
}