import Field from "./Field.jsx";

export default function NameResult({ name }) {
  if (!name) return null;
  const chipClass =
    name.entity_type === "business"
      ? "business"
      : name.entity_type === "household"
      ? "household"
      : "person";

  return (
    <div className="card">
      <h2>
        Name
        <span className={`chip ${chipClass}`}>
          {name.is_business ? "BUSINESS / COMMERCIAL" : name.entity_type.toUpperCase()}
        </span>
      </h2>

      {name.is_business ? (
        <div className="fields">
          <Field label="Business Name" value={name.business_name} />
        </div>
      ) : (
        <div className="fields">
          <Field label="Prefix" value={name.prefix} />
          <Field label="First" value={name.first} />
          <Field label="Middle" value={name.middle} />
          <Field label="Last" value={name.last} />
          <Field label="Suffix" value={name.suffix} />
          <Field label="Nickname" value={name.nickname} />
        </div>
      )}
      <div className="examples">Confidence: {(name.confidence * 100).toFixed(0)}%</div>
    </div>
  );
}
