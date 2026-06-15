export default function Field({ label, value }) {
  const empty = value === null || value === undefined || value === "";
  return (
    <div className="field">
      <div className="k">{label}</div>
      <div className={`v${empty ? " empty" : ""}`}>{empty ? "—" : value}</div>
    </div>
  );
}
