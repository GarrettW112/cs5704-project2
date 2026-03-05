import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageLayout from "../components/PageLayout";

const API_BASE = "http://127.0.0.1:8000";

function Home() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  async function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setError("");
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/receipts/process-receipt/`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.text();
        throw new Error(detail || "Receipt processing failed");
      }

      const receipt = await res.json();
      navigate(`/past-uploads/${receipt.receipt_id}?fromUpload=1`);
    } catch (err) {
      setError("Could not process receipt. Please try again.");
      console.error(err);
    } finally {
      setIsUploading(false);
      e.target.value = "";
    }
  }

  return (
    <PageLayout>
      <section className="hero">
        <h1>Track groceries. Save money. Reduce waste.</h1>
        <p>
          Upload a receipt and instantly see your spending breakdown and updated
          inventory.
        </p>

        <label className="upload-cta">
          <input
            type="file"
            accept="image/*"
            hidden
            disabled={isUploading}
            onChange={handleFileChange}
          />
          {isUploading ? "Processing..." : "Upload A Receipt"}
        </label>

        {error ? <p className="text-red-600 mt-3">{error}</p> : null}
      </section>

      <section className="how">
        <h2>How it works</h2>

        <div className="how-grid">
          <article className="how-card">
            <img src="/images/step-upload.png" alt="Upload receipt" />
            <h3>1. Upload your receipt</h3>
            <p>Take a photo or upload an image.</p>
          </article>

          <article className="how-card">
            <img src="/images/step-insights.png" alt="AI insights" />
            <h3>2. Review AI insights</h3>
            <p>See categorized spending + expiration estimates.</p>
          </article>

          <article className="how-card">
            <img src="/images/step-inventory.png" alt="Manage inventory" />
            <h3>3. Manage your inventory</h3>
            <p>Track what you have and avoid waste.</p>
          </article>
        </div>
      </section>
    </PageLayout>
  );
}

export default Home;