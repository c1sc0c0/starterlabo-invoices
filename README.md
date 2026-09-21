# Starters Labo — invoices skill

Unofficial [Cursor](https://cursor.com) / [Claude Code](https://code.claude.com) skill that creates **Nieuwe verkoopfactuur** drafts on [mijn.starterslabo.be](https://mijn.starterslabo.be) with Playwright (**Opslaan als concept** by default).

Not affiliated with Starterslabo. You need your own portal login. Credentials are never stored in this repo.

## Install

Clone this repo **as the skill folder** (it must contain `SKILL.md` at the root):

```bash
# Cursor — this project
git clone https://github.com/c1sc0c0/starterlabo-invoices.git .cursor/skills/starterlabo-invoices

# Cursor — all projects
git clone https://github.com/c1sc0c0/starterlabo-invoices.git ~/.cursor/skills/starterlabo-invoices

# Claude Code — this project
git clone https://github.com/c1sc0c0/starterlabo-invoices.git .claude/skills/starterlabo-invoices

# Claude Code — all projects
git clone https://github.com/c1sc0c0/starterlabo-invoices.git ~/.claude/skills/starterlabo-invoices
```

Start a new agent chat so the skill is picked up.

**Claude.ai:** zip this folder (with `SKILL.md` at the zip root) and upload it as a custom skill.

## Setup (once)

```bash
cd /path/to/starterlabo-invoices
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/playwright install chromium
```

Credentials via env (preferred) or a local `scripts/.env` copied from `scripts/.env.example` (gitignored):

```bash
export STARTERSLABO_EMAIL='you@example.com'
export STARTERSLABO_PASSWORD='your-password'
```

## Use

Tell the agent something like:

> Maak een concept verkoopfactuur voor Jane Doe particulier, Example Street 1, 1000 Brussels, customer@example.com — Consulting service €100 excl. 21% BTW.

The agent should dry-run `scripts/create_draft_invoice.py`, show totals, then save as concept after you confirm.

## Manual dry-run

```bash
cd /path/to/starterlabo-invoices
STARTERSLABO_EMAIL='you@example.com' STARTERSLABO_PASSWORD='your-password' \
  .venv/bin/python scripts/create_draft_invoice.py \
  --name "Jane Doe" \
  --email "customer@example.com" \
  --address "Example Street 1" \
  --city "Brussels" \
  --postal "1000" \
  --description "Consulting service" \
  --price 100 \
  --vat 21 \
  --dry-run
```

Omit `--dry-run` to **Opslaan als concept**. Never pass `--send` unless you intend to submit for coach review.

## Privacy

- No real credentials, customer PII, or screenshots in this repo.
- `.gitignore` excludes `.env`, `.venv/`, and `draft-invoice-*.png`.
- Do not paste portal passwords into public issues/PRs.

## Related

- [starterslabo-faq](https://github.com/c1sc0c0/starterslabo-faq) — crawl portal FAQ
- [starterslabo-eval](https://github.com/c1sc0c0/starterslabo-eval) — fill monthly evaluatiefiche

## License

MIT for this skill’s code and instructions. Starterslabo’s website and portal remain theirs.
