type Props = {
  receiptId: string;
  receiptType: string;
};

export function ReceiptPanel({ receiptId, receiptType }: Props) {
  if (!receiptId) return null;
  return (
    <section className="panel receipt">
      <h2>Gensyn Receipt</h2>
      <p className="receipt-type">{receiptType === "gensyn_ree" ? "REE cryptographic receipt" : "Deterministic SHA256 receipt (fallback)"}</p>
      <code className="receipt-hash">{receiptId}</code>
      <p className="muted">Trust, but verify — same inputs produce the same ranked shortlist.</p>
    </section>
  );
}
