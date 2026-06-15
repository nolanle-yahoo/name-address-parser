import Constants from "expo-constants";
import { Platform } from "react-native";

// On Android emulator, localhost refers to the emulator itself; 10.0.2.2 maps
// to the host machine. Adjust apiUrl in app.json for a physical device (use
// your computer's LAN IP, e.g. http://192.168.1.20:8000).
function resolveBaseUrl() {
  const configured = Constants.expoConfig?.extra?.apiUrl || "http://localhost:8000";
  if (Platform.OS === "android" && configured.includes("localhost")) {
    return configured.replace("localhost", "10.0.2.2");
  }
  return configured;
}

const API_URL = resolveBaseUrl();

async function post(path, body) {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  parseFull: (name, address, validate_address = true) =>
    post("/api/parse", { name, address, validate_address }),
  health: async () => (await fetch(`${API_URL}/health`)).json(),
  baseUrl: API_URL,
};
