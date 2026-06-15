const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function post(path, body) {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  parseName: (name) => post("/api/parse/name", { name }),
  parseAddress: (address) => post("/api/parse/address", { address }),
  validateAddress: (payload) => post("/api/validate/address", payload),
  parseFull: (name, address, validate_address = true) =>
    post("/api/parse", { name, address, validate_address }),
  health: async () => {
    const res = await fetch(`${API_URL}/health`);
    return res.json();
  },
};
