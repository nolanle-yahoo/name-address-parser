import { useEffect, useState } from "react";
import { api } from "./api.js";
import NameResult from "./components/NameResult.jsx";
import AddressResult from "./components/AddressResult.jsx";

const NAME_EXAMPLES = [
  "Dr. John A. Smith Jr.",
  "Maria Garcia-Lopez",
  "Acme Plumbing & Supply LLC",
];
const ADDR_EXAMPLES = [
  "1600 Pennsylvania Ave NW Suite 200, Washington, DC 20500",
  "123 N Main St Apt 4B, Springfield, IL 62701-1234",
  "PO Box 123, Reno, NV 89501",
];

export default function App() {
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [validate, setValidate] = useState(true);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [provider, setProvider] = useState("");

  useEffect(() => {
    api.health().then((h) => setProvider(h.validator)).catch(() => {});
  }, []);

  async function onParse() {
    setError("");
    if (!name && !address) {
      setError("Enter a name and/or an address.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.parseFull(name || null, address || null, validate);
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function clearAll() {
    setName("");
    setAddress("");
    setResult(null);
    setError("");
  }

  return (
    <div className="container">
      <header>
        <h1>Name &amp; Address Parser / Validator</h1>
        <p>Parse US consumer &amp; business names and US mailing addresses into components.</p>
      </header>
      <div className="status">
        Address validation provider: <b>{provider || "…"}</b>
        {provider === "mock" && " (offline structural check — set USPS/Smarty keys for true verification)"}
      </div>

      <div className="card">
        <h2>Input</h2>
        <label>Name (person or business)</label>
        <input
          type="text"
          value={name}
          placeholder="e.g. Dr. John A. Smith Jr."
          onChange={(e) => setName(e.target.value)}
        />
        <div className="examples">
          Try:{" "}
          {NAME_EXAMPLES.map((ex, i) => (
            <span key={ex}>
              <a onClick={() => setName(ex)}>{ex}</a>
              {i < NAME_EXAMPLES.length - 1 ? " · " : ""}
            </span>
          ))}
        </div>

        <label style={{ marginTop: 16 }}>Address</label>
        <textarea
          value={address}
          placeholder="e.g. 1600 Pennsylvania Ave NW Suite 200, Washington, DC 20500"
          onChange={(e) => setAddress(e.target.value)}
        />
        <div className="examples">
          Try:{" "}
          {ADDR_EXAMPLES.map((ex, i) => (
            <span key={ex}>
              <a onClick={() => setAddress(ex)}>{ex}</a>
              {i < ADDR_EXAMPLES.length - 1 ? " · " : ""}
            </span>
          ))}
        </div>

        <label style={{ marginTop: 16 }}>
          <input
            type="checkbox"
            checked={validate}
            onChange={(e) => setValidate(e.target.checked)}
            style={{ width: "auto", marginRight: 8 }}
          />
          Validate address for US mailing
        </label>

        <div className="row">
          <button onClick={onParse} disabled={loading}>
            {loading ? "Parsing…" : "Parse & Validate"}
          </button>
          <button className="secondary" onClick={clearAll}>
            Clear
          </button>
        </div>
        {error && <div className="error">{error}</div>}
      </div>

      {result && (
        <>
          <NameResult name={result.name} />
          <AddressResult address={result.address} validation={result.validation} />
        </>
      )}

      <footer>
        Parsing by <code>probablepeople</code> &amp; <code>usaddress</code> · Validation via USPS / Smarty
      </footer>
    </div>
  );
}
