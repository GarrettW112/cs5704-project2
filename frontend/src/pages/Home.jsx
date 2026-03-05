import PageLayout from "../components/PageLayout";

function Home() {
  return (
    <PageLayout>
      <section className="hero">
        <h1>Track groceries. Save money. Reduce waste.</h1>
        <p>
          Upload a receipt and instantly see your spending breakdown and updated inventory.
        </p>

        <label className="upload-cta">
          <input type="file" accept="image/*" hidden />
          Upload A Receipt
        </label>
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