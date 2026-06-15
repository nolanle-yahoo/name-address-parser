import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors } from "./theme";

export function Field({ label, value }) {
  const empty = value === null || value === undefined || value === "";
  return (
    <View style={styles.field}>
      <Text style={styles.fieldKey}>{label.toUpperCase()}</Text>
      <Text style={[styles.fieldVal, empty && styles.empty]}>{empty ? "—" : String(value)}</Text>
    </View>
  );
}

export function Chip({ text, type }) {
  const tint =
    type === "business" ? colors.amber : type === "household" ? colors.muted : colors.accent;
  return (
    <View style={[styles.chip, { backgroundColor: tint + "30" }]}>
      <Text style={[styles.chipText, { color: tint }]}>{text}</Text>
    </View>
  );
}

export function Card({ title, right, children }) {
  return (
    <View style={styles.card}>
      {title ? (
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>{title}</Text>
          {right}
        </View>
      ) : null}
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  cardHeader: { flexDirection: "row", alignItems: "center", marginBottom: 12 },
  cardTitle: { color: colors.text, fontSize: 17, fontWeight: "700" },
  field: {
    backgroundColor: colors.card2,
    borderRadius: 8,
    padding: 10,
    marginBottom: 8,
    width: "48%",
  },
  fieldKey: { color: colors.muted, fontSize: 10, letterSpacing: 0.5, marginBottom: 2 },
  fieldVal: { color: colors.text, fontSize: 14 },
  empty: { color: "#64748b", fontStyle: "italic" },
  chip: { marginLeft: 8, paddingHorizontal: 10, paddingVertical: 3, borderRadius: 999 },
  chipText: { fontSize: 11, fontWeight: "700" },
});
