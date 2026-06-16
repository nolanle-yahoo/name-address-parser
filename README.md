# Name / Address Parser & Validator

Parses **US consumer and business names** and **US mailing addresses** into their
individual components, and validates addresses for US mailing using an external
provider (USPS Web Tools or Smarty), with an offline fallback so it runs out of
the box.

It ships in three parts that share one backend:

```
name-address-parser/
├── backend/   FastAPI service — parsing + validation (the brains)
├── web/       React + Vite web app
└── mobile/    Expo (React Native) mobile app — iOS / Android
```

## What it does

### Name parsing
Powered by [`probablepeople`](https://github.com/datamade/probablepeople), which
both tags name parts **and** classifies the string as a person, household, or
**business/corporation**.

- Person names → `prefix`, `first`, `middle`, `last`, `suffix`, `nickname`
- Business names → flagged `BUSINESS / COMMERCIAL` with the full business name
- Falls back to [`nameparser`](https://github.com/derek73/python-nameparser) if needed

| Input | Result |
|---|---|
| `Dr. John A. Smith Jr.` | person · first=John, middle=A., last=Smith, suffix=Jr. |
| `Acme Plumbing & Supply LLC` | **business / commercial** |
| `Maria Garcia-Lopez` | person · first=Maria, last=Garcia-Lopez |

### Address parsing
Powered by [`usaddress`](https://github.com/datamade/usaddress). Breaks an
address into every mailing element:

`street_number`, `pre_directional`, `street_name`, `street_suffix`,
`post_directional`, `unit_type`, `unit_number`, `po_box`, `city`, `state`,
`zip_code`, `zip_plus4`, plus the detected address type (Street / PO Box).

### Address validation (external)
Confirms the address is a real, mailable US address and returns the
USPS-standardized form. Providers are pluggable via `ADDRESS_VALIDATOR`:

| Provider | Value | Needs | Notes |
|---|---|---|---|
| Mock (default) | `mock` | nothing | offline structural checks — runs out of the box, **not USPS-verified** |
| USPS Web Tools | `usps` | `USPS_USER_ID` | free; official USPS address standardization |
| Smarty | `smarty` | `SMARTY_AUTH_ID`, `SMARTY_AUTH_TOKEN` | DPV deliverability + standardization |
| Nominatim (OpenStreetMap) | `nominatim` | none (set `NOMINATIM_USER_AGENT`) | Free & keyless; OSM **geocoding** match — confirms the address exists, **not** USPS deliverability |

If a provider is selected but credentials are missing, it degrades gracefully to
the mock validator.

---

## 1. Backend (required)

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate     macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit to pick a provider / add keys (optional)
python run.py               # serves http://localhost:8000  (docs at /docs)
```

Key endpoints:
- `POST /api/parse/name` — `{ "name": "..." }`
- `POST /api/parse/address` — `{ "address": "..." }`
- `POST /api/validate/address` — `{ "street","city","state","zip_code","secondary" }`
- `POST /api/parse` — combined: `{ "name","address","validate_address" }`
- `GET /health`

### Enabling real validation
USPS (free): register at <https://www.usps.com/business/web-tools-apis/>, then in `.env`:
```
ADDRESS_VALIDATOR=usps
USPS_USER_ID=your_user_id
```
Smarty: create a US Street API key pair at <https://www.smarty.com/>, then:
```
ADDRESS_VALIDATOR=smarty
SMARTY_AUTH_ID=...
SMARTY_AUTH_TOKEN=...
```

## 2. Web app

```bash
cd web
npm install
cp .env.example .env        # VITE_API_URL defaults to http://localhost:8000
npm run dev                 # http://localhost:5173
```

## 3. Mobile app (Expo)

```bash
cd mobile
npm install
npm start                   # scan QR with Expo Go, or press a / i for emulator
```

- The API URL is set in `mobile/app.json` → `expo.extra.apiUrl`.
- On the **Android emulator**, `localhost` is auto-rewritten to `10.0.2.2`.
- On a **physical device**, set `apiUrl` to your computer's LAN IP, e.g.
  `http://192.168.1.20:8000` (the device and computer must share a network).

---

## Architecture notes
- All parsing/validation logic lives in the **backend** so the web and mobile
  clients stay thin and always agree.
- The validator is behind an `AddressValidator` interface
  (`backend/app/validators/`), so adding Google, Lob, or Melissa is a single
  new class + a line in `factory.py`.
