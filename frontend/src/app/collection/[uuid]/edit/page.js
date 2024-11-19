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
        // Fetch existing collection data
        const fetchCollection = async () => {
            try {
                const res = await fetch(`http://localhost:5000/api/collection/${uuid}/edit`, {
                    credentials: "include"
                });

                if (res.status === 401) {
                    router.push("/login");
                } else if (res.status === 403) {
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

    const addExhibit = () => {
        setExhibits([...exhibits, { title: "", url: "", exhibit_format: "", text: "", font: "" }]);
    };

    const removeExhibit = (index) => {
        setExhibits(exhibits.filter((_, i) => i !== index));
    };

    const handleExhibitChange = (index, field, value) => {
        const newExhibits = [...exhibits];
        if (field === "font") {
            const validFonts = ["sans", "serif", "mono"];
            if (!validFonts.includes(value)) {
                setError("Invalid font. Only 'sans', 'serif', and 'mono' are allowed.");
                return;
            } else {
                setError(null); // Clear any previous error
            }
        }

        // Ensure exhibit_format is capitalized
        if (field === "exhibit_format") {
            value = value.charAt(0).toUpperCase() + value.slice(1);
        }

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
                <div key={index} className="mb-4 p-4 bg-white border border-gray-200 rounded-md shadow-sm relative">
                    <button
                        className="absolute top-2 right-2 text-red-500 hover:text-red-700"
                        onClick={() => removeExhibit(index)}
                    >
                        &times;
                    </button>
                    <div className="mb-2">
                        <input
                            type="text"
                            placeholder="Title"
                            className="w-full p-2 border border-gray-300 rounded-md"
                            value={exhibit.title}
                            onChange={(e) => handleExhibitChange(index, "title", e.target.value)}
                        />
                    </div>
                    <div className="mb-2">
                        <label className="block text-sm font-medium mb-1">Exhibit Format:</label>
                        <select
                            className="w-full p-2 border border-gray-300 rounded-md"
                            value={exhibit.exhibit_format}
                            onChange={(e) => handleExhibitChange(index, "exhibit_format", e.target.value)}
                        >
                            <option value="">Select Format</option>
                            <option value="Images">Images</option>
                            <option value="Videos">Videos</option>
                            <option value="Embeds">Embeds</option>
                            <option value="Texts">Texts</option>
                        </select>
                    </div>

                    {(exhibit.exhibit_format === "Images" || exhibit.exhibit_format === "Videos" || exhibit.exhibit_format === "Embeds") && (
                        <div className="mb-2">
                            <input
                                type="text"
                                placeholder="URL"
                                className="w-full p-2 border border-gray-300 rounded-md"
                                value={exhibit.url}
                                onChange={(e) => handleExhibitChange(index, "url", e.target.value)}
                            />
                        </div>
                    )}

                    {exhibit.exhibit_format === "Texts" && (
                        <>
                            <div className="mb-2">
                                <input
                                    type="text"
                                    placeholder="Text"
                                    className="w-full p-2 border border-gray-300 rounded-md"
                                    value={exhibit.text}
                                    onChange={(e) => handleExhibitChange(index, "text", e.target.value)}
                                />
                            </div>
                            <div className="mb-2">
                                <label className="block text-sm font-medium mb-1">Font:</label>
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
                            </div>
                        </>
                    )}
                </div>
            ))}

            <button
                className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 mb-4"
                onClick={addExhibit}
            >
                Add Exhibit
            </button>

            <button
                className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600"
                onClick={handleSubmit}
            >
                Save Changes
            </button>

            {error && <p className="text-red-500 mt-4">{error}</p>}
        </div>
    );
}