import PageLayout from "../components/PageLayout";

const receipts = [
  { id: 1, store: "Kroger", date: "2026-03-03" },
  { id: 2, store: "Walmart", date: "2026-03-01" },
  { id: 3, store: "Trader Joe's", date: "2026-02-28" },
];

function ReceiptRow({ store, date }) {
  return (
    <li className="receipt-row">
      <span className="receipt-store">{store}</span>
      <span className="receipt-date">{date}</span>
    </li>
  );
}

function ReceiptList({ items }) {
  if (!items.length) return <p className="receipt-empty">No uploads yet.</p>;

  return (
    <ul className="receipt-list">
      {items.map((receipt) => (
        <ReceiptRow
          key={receipt.id}
          store={receipt.store}
          date={receipt.date}
        />
      ))}
    </ul>
  );
}

function PastUploads() {
  return (
    <PageLayout>
      <section className="past-uploads">
        <h1>Past Uploads</h1>
        <p className="past-uploads-subtext">
          Your receipts by store and date.
        </p>
        <ReceiptList items={receipts} />
      </section>
    </PageLayout>
  );
}

export default PastUploads;