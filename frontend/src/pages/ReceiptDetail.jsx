import PageLayout from "../components/PageLayout";
import { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from "react-router-dom";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, Label } from 'recharts';

function ReceiptDetail() {
    const { id } = useParams();
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingItem, setEditingItem] = useState(null); // null = adding new

    const token = localStorage.getItem("access_token");
    const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

    // --- API CALLS ---
    const fetchReceipt = async () => {
        try {
            const response = await fetch(`http://localhost:8000/receipts/${id}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!response.ok) throw new Error('Failed to fetch');
            const result = await response.json();
            setData(result);
        } catch (err) { setError(err.message); }
    };

    const handleDelete = async (itemId) => {
        if (!window.confirm("Delete this item?")) return;
        try {
            await fetch(`http://localhost:8000/items/${itemId}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` },
            });
            // Update local state without re-fetching everything
            setData({ ...data, items: data.items.filter(i => i.id !== itemId) });
        } catch (err) { alert("Delete failed"); }
    };

    const currentTotal = useMemo(() => {
        if (!data?.items) return 0;
        return data.items.reduce((sum, item) => {
            return sum + (Number(item.price || 0) * Number(item.quantity || 1));
        }, 0);
    }, [data]);

    const handleSaveItem = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const formProps = Object.fromEntries(formData);

        // Prepare the payload to match ItemCreate schema
        const itemPayload = {
            // 1. Backend REQUIRES raw_name. If editing, we keep the old one, 
            // if new, we use the name provided.
            raw_name: editingItem?.raw_name || formProps.normalized_name,
            normalized_name: formProps.normalized_name || null,

            // 2. Convert empty strings to null so Pydantic is happy
            category: formProps.category || null,

            // 3. Ensure numbers are actual Numbers, not strings
            price: parseFloat(formProps.price),
            quantity: parseFloat(formProps.quantity || 1),

            // 4. Handle the Date string specifically
            estimated_expiration_date: formProps.estimated_expiration_date || null,

            // 5. Link to the current receipt
            receipt_id: parseInt(id)
        };

        const url = editingItem
            ? `http://localhost:8000/items/${editingItem.id}`
            : `http://localhost:8000/items`;

        const method = editingItem ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(itemPayload)
            });

            if (!response.ok) {
                const errorDetail = await response.json();
                console.error("Validation Error Details:", errorDetail);
                throw new Error('Save failed');
            }

            setIsModalOpen(false);
            fetchReceipt();
        } catch (err) {
            alert("Error saving item. Check console for details.");
        }
    };

    useEffect(() => { if (id) fetchReceipt(); }, [id]);

    // --- CHART LOGIC ---
    const chartData = useMemo(() => {
        if (!data?.items) return [];
        const categories = data.items.reduce((acc, item) => {
            const cat = item.category || "Uncategorized";
            acc[cat] = (acc[cat] || 0) + (Number(item.price) * Number(item.quantity));
            return acc;
        }, {});
        return Object.keys(categories).map(key => ({ name: key, value: parseFloat(categories[key].toFixed(2)) }));
    }, [data]);

    const getExpirationStatus = (dateString) => {
        if (!dateString) return { label: "No Date", color: "text-slate-400 bg-slate-50" };
        const diffDays = Math.ceil((new Date(dateString) - new Date()) / (1000 * 60 * 60 * 24));
        if (diffDays < 0) return { label: "Expired", color: "text-red-700 bg-red-50" };
        return { label: new Date(dateString).toLocaleDateString(), color: "text-slate-600 bg-slate-50" };
    };

    if (error) return <PageLayout><div>Error: {error}</div></PageLayout>;
    if (!data) return <PageLayout><div>Loading...</div></PageLayout>;

    return (
        <PageLayout>
            <div className="max-w-5xl mx-auto space-y-8 p-4 pb-20">
                {/* Header */}
                <div className="flex justify-between items-center border-b pb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900">{data.store}</h1>
                        <p className="text-slate-500">{new Date(data.purchase_date).toLocaleDateString()}</p>
                    </div>
                    <button
                        onClick={() => { setEditingItem(null); setIsModalOpen(true); }}
                        className="bg-blue-600 text-white px-4 py-2 rounded-xl font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-200"
                    >
                        + Add Item
                    </button>
                </div>

                {/* Pie Chart Card */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={chartData}
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {chartData.map((_, i) => (
                                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                                ))}

                                {/* DYNAMIC CENTER LABEL */}
                                <Label
                                    value={`$${currentTotal.toFixed(2)}`}
                                    position="center"
                                    className="text-2xl font-black fill-slate-900"
                                    style={{ fontSize: '24px', fontWeight: '900' }}
                                />
                            </Pie>

                            <Tooltip
                                formatter={(value, name, props) => {
                                    const percent = props.payload?.percent
                                        ? (props.payload.percent * 100).toFixed(1)
                                        : "0";
                                    return [`$${Number(value).toFixed(2)} (${percent}%)`, name];
                                }}
                            />
                            <Legend verticalAlign="bottom" height={36} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Table */}
                <div className="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
                    <table className="w-full text-left">
                        <thead className="bg-slate-50 border-b border-slate-100">
                            <tr>
                                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase">Item</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase">Price</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase">Expires</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {data.items?.map((item) => {
                                const expiry = getExpirationStatus(item.estimated_expiration_date);
                                return (
                                    <tr key={item.id} className="hover:bg-slate-50 transition-colors group">
                                        <td className="px-6 py-4">
                                            <p className="font-bold text-slate-800">{item.normalized_name || item.raw_name}</p>
                                            <p className="text-xs text-slate-400">{item.category}</p>
                                        </td>
                                        <td className="px-6 py-4 font-medium text-slate-700">
                                            ${Number(item.price).toFixed(2)} <span className="text-xs text-slate-400">x{item.quantity}</span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded-md text-[10px] font-bold border ${expiry.color}`}>
                                                {expiry.label}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right space-x-2">
                                            <button
                                                onClick={() => { setEditingItem(item); setIsModalOpen(true); }}
                                                className="p-2 text-slate-400 hover:text-blue-600 transition-colors"
                                            >
                                                ✏️
                                            </button>
                                            <button
                                                onClick={() => handleDelete(item.id)}
                                                className="p-2 text-slate-400 hover:text-red-600 transition-colors"
                                            >
                                                🗑️
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* --- ADD/EDIT MODAL --- */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 relative">
                        <button onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600">✕</button>
                        <h2 className="text-2xl font-bold mb-6">{editingItem ? 'Edit Item' : 'Add New Item'}</h2>

                        <form onSubmit={handleSaveItem} className="space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Name</label>
                                <input name="normalized_name" defaultValue={editingItem?.normalized_name} className="w-full bg-slate-50 border-none rounded-xl p-3" required />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Price</label>
                                    <input name="price" type="number" step="0.01" defaultValue={editingItem?.price} className="w-full bg-slate-50 border-none rounded-xl p-3" required />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Qty</label>
                                    <input name="quantity" type="number" defaultValue={editingItem?.quantity || 1} className="w-full bg-slate-50 border-none rounded-xl p-3" required />
                                </div>
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Category</label>
                                <input name="category" defaultValue={editingItem?.category} className="w-full bg-slate-50 border-none rounded-xl p-3" />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Expiration Date</label>
                                <input name="estimated_expiration_date" type="date" defaultValue={editingItem?.estimated_expiration_date?.split('T')[0]} className="w-full bg-slate-50 border-none rounded-xl p-3" />
                            </div>
                            <button type="submit" className="w-full bg-slate-900 text-white font-bold py-4 rounded-2xl hover:bg-slate-800 transition-all mt-4">
                                Save Changes
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </PageLayout>
    );
}

export default ReceiptDetail;