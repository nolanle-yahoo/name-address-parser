import React, { useEffect, useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Switch,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { api } from "./src/api";
import { colors } from "./src/theme";
import { Card, Field, Chip } from "./src/components";

export default function App() {
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [validate, setValidate] = useState(true);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [provider, setProvider] = useState("");

  useEffect(() => {
    api.health().then((h) => setProvider(h.validator)).catch(() => setProvider("unreachable"));
  }, []);

  async function onParse() {
    setError("");
    if (!name && !address) {
      setError("Enter a name and/or an address.");
      return;
    }
    setLoading(true);
    try {
      setResult(await api.parseFull(name || null, address || null, validate));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const nm = result?.name;
  const ad = result?.address;
  const val = result?.validation;

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.h1}>Name &amp; Address Parser</Text>
        <Text style={styles.sub}>Parse US names &amp; addresses · validate for mailing</Text>
        <Text style={styles.status}>
          Validator: <Text style={{ color: colors.accent }}>{provider || "…"}</Text>
        </Text>

        <Card title="Input">
          <Text style={styles.label}>Name (person or business)</Text>
          <TextInput
            style={styles.input}
            value={name}
            onChangeText={setName}
            placeholder="Dr. John A. Smith Jr."
            placeholderTextColor="#64748b"
          />
          <Text style={[styles.label, { marginTop: 14 }]}>Address</Text>
          <TextInput
            style={[styles.input, styles.multiline]}
            value={address}
            onChangeText={setAddress}
            placeholder="1600 Pennsylvania Ave NW Suite 200, Washington, DC 20500"
            placeholderTextColor="#64748b"
            multiline
          />
          <View style={styles.switchRow}>
            <Switch value={validate} onValueChange={setValidate} />
            <Text style={styles.switchLabel}>Validate address for US mailing</Text>
          </View>
          <TouchableOpacity style={styles.button} onPress={onParse} disabled={loading}>
            {loading ? (
              <ActivityIndicator color="#04293a" />
            ) : (
              <Text style={styles.buttonText}>Parse &amp; Validate</Text>
            )}
          </TouchableOpacity>
          {!!error && <Text style={styles.error}>{error}</Text>}
        </Card>

        {nm && (
          <Card
            title="Name"
            right={
              <Chip
                type={nm.is_business ? "business" : nm.entity_type}
                text={nm.is_business ? "BUSINESS / COMMERCIAL" : nm.entity_type.toUpperCase()}
              />
            }
          >
            <View style={styles.grid}>
              {nm.is_business ? (
                <Field label="Business Name" value={nm.business_name} />
              ) : (
                <>
                  <Field label="Prefix" value={nm.prefix} />
                  <Field label="First" value={nm.first} />
                  <Field label="Middle" value={nm.middle} />
                  <Field label="Last" value={nm.last} />
                  <Field label="Suffix" value={nm.suffix} />
                  <Field label="Nickname" value={nm.nickname} />
                </>
              )}
            </View>
          </Card>
        )}

        {ad && (
          <Card title="Address" right={<Chip type="household" text={ad.address_type} />}>
            <View style={styles.grid}>
              <Field label="Street #" value={ad.street_number} />
              <Field label="Pre-Dir" value={ad.pre_directional} />
              <Field label="Street Name" value={ad.street_name} />
              <Field label="Suffix" value={ad.street_suffix} />
              <Field label="Post-Dir" value={ad.post_directional} />
              <Field label="Unit Type" value={ad.unit_type} />
              <Field label="Unit #" value={ad.unit_number} />
              <Field label="PO Box" value={ad.po_box} />
              <Field label="City" value={ad.city} />
              <Field label="State" value={ad.state} />
              <Field label="ZIP" value={ad.zip_code} />
              <Field label="ZIP+4" value={ad.zip_plus4} />
            </View>

            {val && (
              <View
                style={[
                  styles.banner,
                  { borderColor: val.is_valid ? colors.green : colors.red },
                ]}
              >
                <Text style={{ color: val.is_valid ? "#bbf7d0" : "#fecaca", fontWeight: "700" }}>
                  {val.is_valid ? "✓ Valid mailing address" : "✗ Could not validate"} ({val.provider})
                </Text>
                {val.is_valid && val.standardized_street ? (
                  <Text style={styles.bannerText}>
                    {val.standardized_street}
                    {val.standardized_secondary ? ` ${val.standardized_secondary}` : ""},{" "}
                    {val.standardized_city} {val.standardized_state} {val.standardized_zip}
                    {val.standardized_zip4 ? `-${val.standardized_zip4}` : ""}
                  </Text>
                ) : null}
                {val.messages?.map((m, i) => (
                  <Text key={i} style={styles.bannerText}>• {m}</Text>
                ))}
              </View>
            )}
          </Card>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  container: { padding: 16, paddingBottom: 48 },
  h1: { color: colors.text, fontSize: 24, fontWeight: "800" },
  sub: { color: colors.muted, marginTop: 2, marginBottom: 6 },
  status: { color: colors.muted, fontSize: 12, marginBottom: 14 },
  label: { color: colors.muted, fontSize: 13, marginBottom: 6 },
  input: {
    backgroundColor: colors.bg,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    color: colors.text,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
  },
  multiline: { minHeight: 64, textAlignVertical: "top" },
  switchRow: { flexDirection: "row", alignItems: "center", marginTop: 14 },
  switchLabel: { color: colors.text, marginLeft: 10 },
  button: {
    backgroundColor: colors.accent,
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: "center",
    marginTop: 16,
  },
  buttonText: { color: "#04293a", fontWeight: "700", fontSize: 15 },
  error: { color: colors.red, marginTop: 10 },
  grid: { flexDirection: "row", flexWrap: "wrap", justifyContent: "space-between" },
  banner: { borderWidth: 1, borderRadius: 8, padding: 10, marginTop: 12 },
  bannerText: { color: colors.text, fontSize: 13, marginTop: 4 },
});
