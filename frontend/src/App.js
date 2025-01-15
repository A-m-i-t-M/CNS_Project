import React, { useState } from "react";

function App() {
    const [rules, setRules] = useState([]);
    const [rule, setRule] = useState({ action: "", src_ip: "", port: "", protocol: "", size_min: 0, size_max: 0 });
    const [isEditing, setIsEditing] = useState(false);
    const [editIndex, setEditIndex] = useState(null);

    const fetchRules = async () => {
        const res = await fetch("http://127.0.0.1:8000/rules", {
            method: "GET",
        });
        const data = await res.json();
        setRules(data);
    };

    const addOrUpdateRule = async () => {
        if (isEditing) {
            // Update existing rule
            await fetch(`http://127.0.0.1:8000/rules/${editIndex}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(rule),
            });
            setIsEditing(false);
            setEditIndex(null);
        } else {
            // Add new rule
            await fetch("http://127.0.0.1:8000/rules", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(rule),
            });
        }
        setRule({ action: "", src_ip: "", port: "", protocol: "", size_min: 0, size_max: 0 });
        fetchRules();
    };

    const deleteRule = async (index) => {
        await fetch(`http://127.0.0.1:8000/rules/${index}`, {
            method: "DELETE",
        });
        fetchRules();
    };

    const editRule = (index) => {
        setRule(rules[index]);
        setIsEditing(true);
        setEditIndex(index);
    };

    return (
        <div className="flex flex-col items-center p-6 space-y-6 bg-gray-100 min-h-screen">
            <h1 className="text-4xl font-bold text-gray-800">Personalized Firewall</h1>
            
            <button 
                onClick={fetchRules} 
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-200"
            >
                Fetch Rules
            </button>

            <div className="space-y-4 w-full max-w-md bg-white p-6 rounded-lg shadow-lg">
                <h2 className="text-2xl font-semibold text-gray-700 mb-4">
                    {isEditing ? "Update Rule" : "Add New Rule"}
                </h2>
                
                <input 
                    placeholder="Action" 
                    value={rule.action}
                    onChange={(e) => setRule({ ...rule, action: e.target.value })}
                    className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input 
                    placeholder="Source IP" 
                    value={rule.src_ip}
                    onChange={(e) => setRule({ ...rule, src_ip: e.target.value })}
                    className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input 
                    placeholder="Port" 
                    value={rule.port}
                    onChange={(e) => setRule({ ...rule, port: e.target.value })}
                    className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input 
                    placeholder="Protocol" 
                    value={rule.protocol}
                    onChange={(e) => setRule({ ...rule, protocol: e.target.value })}
                    className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input 
                    placeholder="Min Size" 
                    value={rule.size_min}
                    onChange={(e) => setRule({ ...rule, size_min: parseInt(e.target.value) })}
                    className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input 
                    placeholder="Max Size" 
                    value={rule.size_max}
                    onChange={(e) => setRule({ ...rule, size_max: parseInt(e.target.value) })}
                    className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                
                <button 
                    onClick={addOrUpdateRule} 
                    className={`w-full px-4 py-2 ${isEditing ? "bg-yellow-600" : "bg-green-600"} text-white rounded-lg hover:${isEditing ? "bg-yellow-700" : "bg-green-700"} transition duration-200`}
                >
                    {isEditing ? "Update Rule" : "Add Rule"}
                </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-5xl">
                {rules.map((r, index) => (
                    <div key={r.id} className="bg-white p-4 border border-gray-300 rounded-lg shadow-md">
                        <h3 className="text-xl font-semibold text-gray-800">Rule {index + 1}</h3>
                        <div className="space-y-2 mt-4">
                            <div><strong>Action:</strong> {r.action || "Not specified"}</div>
                            <div><strong>Source IP:</strong> {r.src_ip || "Not specified"}</div>
                            <div><strong>Port:</strong> {r.port || "Not specified"}</div>
                            <div><strong>Protocol:</strong> {r.protocol || "Not specified"}</div>
                            <div><strong>Min Size:</strong> {r.size_min || "Not specified"}</div>
                            <div><strong>Max Size:</strong> {r.size_max || "Not specified"}</div>
                        </div>
                        <div className="flex space-x-2 mt-4">
                            <button 
                                onClick={() => editRule(index)} 
                                className="px-3 py-1 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600"
                            >
                                Edit
                            </button>
                            <button 
                                onClick={() => deleteRule(index)} 
                                className="px-3 py-1 bg-red-500 text-white rounded-lg hover:bg-red-600"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;
