import Field from "./Field.jsx";

export default function AddressResult({ address, validation }) {
  if (!address) return null;
  return (
    <div className="card">
      <h2>
        Address
        <span className="chip household">{address.address_type}</span>
      </h2>
      <div className="fields">
        <Field label="Street Number" value={address.street_number} />
        <Field label="Pre-Directional" value={address.pre_directional} />
        <Field label="Street Name" value={address.street_name} />
        <Field label="Street Suffix" value={address.street_suffix} />
        <Field label="Post-Directional" value={address.post_directional} />
        <Field label="Unit Type" value={address.unit_type} />
        <Field label="Unit Number" value={address.unit_number} />
        <Field label="PO Box" value={address.po_box} />
        <Field label="City" value={address.city} />
        <Field label="State" value={address.state} />
        <Field label="ZIP" value={address.zip_code} />
        <Field label="ZIP+4" value={address.zip_plus4} />
      </div>

      {validation && (
        <div className={`banner ${validation.is_valid ? "ok" : "bad"}`}>
          <div>
            <b>
              {validation.is_valid
                ? "✓ Valid mailing address"
                : "✗ Could not validate address"}
            </b>{" "}
            <span style={{ opacity: 0.8 }}>(provider: {validation.provider})</span>
          </div>
          {validation.is_valid && validation.standardized_street && (
            <div style={{ marginTop: 6 }}>
              <b>USPS standardized:</b> {validation.standardized_street}
              {validation.standardized_secondary
                ? ` ${validation.standardized_secondary}`
                : ""}
              , {validation.standardized_city} {validation.standardized_state}{" "}
              {validation.standardized_zip}
              {validation.standardized_zip4 ? `-${validation.standardized_zip4}` : ""}
            </div>
          )}
          {validation.messages?.length > 0 && (
            <ul>
              {validation.messages.map((m, i) => (
                <li key={i}>{m}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
