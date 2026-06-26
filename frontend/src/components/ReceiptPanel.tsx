type Props = {
  receiptId: string;
  receiptType: string;
};

export function ReceiptPanel({ receiptId, receiptType }: Props) {
  if (!receiptId) return null;
  const label =
    receiptType === "gensyn_ree" || receiptType === "gensyn_ree_local"
      ? "REE cryptographic receipt"
      : "Deterministic SHA256 receipt (fallback)";
  const verifyHint =
    receiptType === "gensyn_ree_local"
      ? "Verify with local Gensyn REE (see receipts path in backend logs)."
      : receiptType === "gensyn_ree"
        ? "Verify via Gensyn REE."
        : "Verify locally: python scripts/verify_receipt.py receipts/<job_id>.json";
  return (
    <section className="panel receipt">
      <h2>Gensyn Receipt</h2>
      <p className="receipt-type">{label}</p>
      <code className="receipt-hash">{receiptId}</code>
      <p className="muted">Trust, but verify — same inputs produce the same ranked shortlist.</p>
      <p className="muted">{verifyHint}</p>
    </section>
  );
}
