# Verkoopfactuur — reference

## Portal paths

| Item | Value |
|------|--------|
| Menu | Verkoop → **Nieuwe verkoopfactuur** |
| URL | `https://mijn.starterslabo.be/Views/SaleForm.aspx` |
| List | `https://mijn.starterslabo.be/Views/Sale.aspx` |

## Form field → CLI

| Portal label | CLI flag | Notes |
|--------------|----------|--------|
| Type klant | (fixed) | Script clicks **Particulier** |
| Naam | `--name` | Required |
| Email | `--email` | Optional but recommended |
| Straat + Huisnummer | `--address` | Required to save |
| Plaats | `--city` | Required |
| Postcode | `--postal` | Required |
| Land | `--country` | Default `BE` |
| Omschrijving | `--description` | Line 0, max 150 |
| Aantal | `--quantity` | RadNumeric |
| Eenheid | `--unit` | Optional |
| Prijs | `--price` | Excl. VAT (toggle forced off) |
| BTW % | `--vat` | `0` / `6` / `12` / `21` |
| Dry run | `--dry-run` | Fill + screenshot, no save |
| Verstuur | `--send` | Avoid unless user asks |

## Playwright selectors (prefix `ctl00_ContentPlaceLabo_SalesForm_`)

| Role | Selector suffix |
|------|-----------------|
| Particulier | `RadioButtonListCustomerType_1` |
| Zakelijk | `RadioButtonListCustomerType_0` |
| Naam / email / adres / city / postal | `InputCustomerName`, `InputCustomerEmail`, `InputCustomerAdress`, `InputCustomerCity`, `InputCustomerPostalCode` |
| Land | `SelectCustomerCountry` |
| Line 0 desc / qty / unit / price | `rptInvoiceItems_ctl00_ItemDescription`, `ItemAmount`, `ItemUnit`, `ItemPrice` |
| Tax included (hidden checkbox) | `rptInvoiceItems_ctl00_CheckBoxTaxIncluded` |
| Tax toggle (click this) | `rptInvoiceItems_ctl00_TaxToggleLabel` |
| VAT % | `rptInvoiceItems_ctl00_SelectTaxRate` |
| Add row / refresh | `btnAddItem`, `btnRefreshInvoice` |
| Save draft / send | `btnSaveConcept`, `btnSubmit` |
| Validation | `ValidationSummary1` |

Implementation: `scripts/create_draft_invoice.py` (`SEL`, `fill_radnumeric`, `safe_fill`).

## Postback pitfalls

- Switching Particulier/Zakelijk, amount/price Tab, VAT select, tax toggle, and refresh each trigger a **full postback**.
- Fill **line item first**, then **customer fields last** (`safe_fill` retries after detach).
- RadNumericTextBox: click → select-all → type → Tab → wait `networkidle`.
- Tax-included switch: real checkbox is hidden; click `TaxToggleLabel`.

## List view

Verkoop list (`Sale.aspx`): look for **Concept**, customer name, total incl. VAT.
