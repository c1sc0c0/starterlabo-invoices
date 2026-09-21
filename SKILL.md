---
name: starterlabo-invoices
description: >-
  Create sales invoices (verkoopfactuur) on mijn.starterslabo.be via Playwright
  automation. Use when the user mentions verkoopfactuur, sales invoice, Nieuwe
  verkoopfactuur, SaleForm, klant factureren, or wants to draft a customer
  invoice (not aankoop/onkosten) on Starters Labo.
---

# Starters Labo — Nieuwe verkoopfactuur

Create customer sales invoices on [mijn.starterslabo.be](https://mijn.starterslabo.be) via **Verkoop → Nieuwe verkoopfactuur** (`SaleForm.aspx`).

Not affiliated with Starterslabo. Never bake credentials into this skill, never print the password, never commit `.env`.

## Verkoop, aankoop, or onkosten?

| Situation | Use |
|-----------|-----|
| Invoice a customer (you get paid) | **Verkoopfactuur** → this skill |
| Supplier invoice / leverancier | Separate purchase-invoice flow (not this skill) |
| Personal expense reimbursement | Separate onkostennota flow (not this skill) |

When unsure, ask the user once.

## Credentials

If the user did not give a username and password in this conversation, ask for them. Prefer one-shot env vars; do not echo the real password back.

```bash
export STARTERSLABO_EMAIL='USER'
export STARTERSLABO_PASSWORD='PASS'
```

Or copy `scripts/.env.example` → `scripts/.env` locally (gitignored).

## Setup (first run)

Resolve this skill’s `scripts/` directory, then:

```bash
cd /path/to/starterlabo-invoices
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/playwright install chromium
```

## Workflow

```
Progress:
- [ ] 1. Confirm this is a sales invoice (not aankoop/onkosten)
- [ ] 2. Gather customer + line item fields
- [ ] 3. Dry-run with --dry-run
- [ ] 4. User confirms totals/screenshot → save concept (omit --dry-run)
```

### 1. Gather (ask if missing)

**Customer (Particulier — script default):**

- **Naam** — `--name` (required)
- **Email** — `--email` (recommended)
- **Straat + huisnummer** — `--address` (required)
- **Plaats** — `--city` (required)
- **Postcode** — `--postal` (required)
- **Land** — `--country` (default `BE`)

**Line item (one row):**

- **Omschrijving** — `--description`
- **Aantal** — `--quantity` (default `1`)
- **Eenheid** — `--unit` (optional)
- **Prijs excl. BTW** — `--price`
- **BTW %** — `--vat` (`0` / `6` / `12` / `21`, default `21`)

Script always sets price as **excl. VAT** (tax-included toggle off).

### 2. Dry run (default before save)

```bash
cd /path/to/starterlabo-invoices
STARTERSLABO_EMAIL='USER' STARTERSLABO_PASSWORD='PASS' \
  .venv/bin/python scripts/create_draft_invoice.py \
  --name "Jane Doe" \
  --email "customer@example.com" \
  --address "Example Street 1" \
  --city "Brussels" \
  --postal "1000" \
  --country BE \
  --description "Consulting service" \
  --quantity 1 \
  --price 100 \
  --vat 21 \
  --dry-run
```

Screenshot: `draft-invoice-filled.png` in the cwd. Check printed totals.

### 3. Save as concept

Same command **without** `--dry-run`, only after user confirms dry-run output/screenshot.

Verify on **Verkoop** list: row **Concept**, customer name, amount incl. VAT.

### 4. Safety

- Default: **Opslaan als concept** only.
- Never **`--send`** (Verstuur) unless the user explicitly asks to submit for coach review.
- Debug browser: `HEADED=1 … python scripts/create_draft_invoice.py ...`

## Scope notes

- Script targets **Particulier**. **Zakelijk** (VAT number) is not automated yet.
- One line item only.
- Address (straat, plaats, postcode) is required; save fails validation without it.
- Fill order matters: line item (amounts/VAT/refresh) **before** customer fields — postbacks wipe earlier text.

## When the user asks to invoice someone

1. Confirm verkoop (not aankoop/onkosten).
2. Collect customer + line fields; propose CLI args in a short table (use placeholders in chat if needed — never paste real portal passwords).
3. Run `--dry-run`; report totals and screenshot path.
4. Save only on confirmation.
5. Confirm Concept row on Verkoop list.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/create_draft_invoice.py` | Fill form, refresh totals, save draft |
| `scripts/session.py` | Login + browser helpers |

Field map and URLs: [reference.md](reference.md).
