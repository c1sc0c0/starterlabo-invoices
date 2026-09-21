#!/usr/bin/env python3
"""
Create a DRAFT sales invoice (Opslaan als concept) on mijn.starterslabo.be.

Safety:
- Only clicks "Opslaan als concept" (btnSaveConcept), never "Verstuur" (btnSubmit),
  unless --send is passed explicitly.
- Use --dry-run to fill the form and report totals WITHOUT saving anything.

Credentials: STARTERSLABO_EMAIL / STARTERSLABO_PASSWORD via env or scripts/.env.
Never commit .env.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from session import load_credentials, login, new_page

SALE_FORM_URL = "https://mijn.starterslabo.be/Views/SaleForm.aspx"

P = "ctl00_ContentPlaceLabo_SalesForm_"
ROW0 = f"{P}rptInvoiceItems_ctl00_"

SEL = {
    "customer_particulier": f"#{P}RadioButtonListCustomerType_1",
    "customer_zakelijk": f"#{P}RadioButtonListCustomerType_0",
    "customer_name": f"#{P}InputCustomerName",
    "customer_email": f"#{P}InputCustomerEmail",
    "customer_address": f"#{P}InputCustomerAdress",
    "customer_city": f"#{P}InputCustomerCity",
    "customer_postal": f"#{P}InputCustomerPostalCode",
    "country": f"#{P}SelectCustomerCountry",
    "add_item": f"#{P}btnAddItem",
    "refresh": f"#{P}btnRefreshInvoice",
    "item_desc": f"#{ROW0}ItemDescription",
    "item_amount": f"#{ROW0}ItemAmount",
    "item_unit": f"#{ROW0}ItemUnit",
    "item_price": f"#{ROW0}ItemPrice",
    "item_tax_incl": f"#{ROW0}CheckBoxTaxIncluded",
    "item_tax_toggle": f"#{ROW0}TaxToggleLabel",
    "item_vat": f"#{ROW0}SelectTaxRate",
    "save_draft": f"#{P}btnSaveConcept",
    "send": f"#{P}btnSubmit",
    "validation_summary": f"#{P}ValidationSummary1",
}


def fill_radnumeric(page: Page, selector: str, value: str) -> None:
    """Fill a Telerik RadNumericTextBox; blur triggers a postback, so wait for it."""
    el = page.locator(selector)
    el.click()
    page.keyboard.press("Control+a")
    page.keyboard.press("Delete")
    el.type(value)
    page.keyboard.press("Tab")
    page.wait_for_load_state("networkidle", timeout=30_000)


def read_totals(page: Page) -> dict[str, str]:
    return page.evaluate(
        """() => {
            const out = {};
            document.querySelectorAll('.row').forEach((r) => {
                const cols = r.querySelectorAll('.col-6');
                if (cols.length === 2) {
                    const label = cols[0].innerText.trim();
                    if (/Totaal/i.test(label)) {
                        out[label] = cols[1].innerText.trim();
                    }
                }
            });
            return out;
        }"""
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Customer name (Particulier)")
    parser.add_argument("--email", default="", help="Customer email")
    parser.add_argument("--address", required=True, help="Street + number (required to save)")
    parser.add_argument("--city", required=True, help="City (required to save)")
    parser.add_argument("--postal", required=True, help="Postal code (required to save)")
    parser.add_argument("--country", default="BE")
    parser.add_argument("--description", default="Consulting service")
    parser.add_argument("--quantity", default="1")
    parser.add_argument("--unit", default="")
    parser.add_argument("--price", default="100", help="Unit price excl. VAT")
    parser.add_argument("--vat", default="21", help="VAT rate: 0/6/12/21")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fill the form but do NOT save anything",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Click Verstuur (final submit) instead of saving a draft. Avoid.",
    )
    args = parser.parse_args()

    email, password = load_credentials()
    out_dir = Path.cwd()

    with sync_playwright() as p:
        browser, page = new_page(p)
        try:
            login(page, email, password)
            page.goto(SALE_FORM_URL, wait_until="networkidle", timeout=60_000)

            # Private customer (postback)
            page.click(SEL["customer_particulier"])
            page.wait_for_load_state("networkidle", timeout=30_000)

            page.select_option(SEL["country"], args.country)

            if page.locator(SEL["item_desc"]).count() == 0:
                page.click(SEL["add_item"])
                page.wait_for_load_state("networkidle", timeout=30_000)

            # Line item first: amount/price/vat/toggle each trigger postbacks that
            # would wipe text typed afterwards, so customer name is filled last.
            page.fill(SEL["item_desc"], args.description)
            if args.unit:
                page.fill(SEL["item_unit"], args.unit)
            fill_radnumeric(page, SEL["item_amount"], args.quantity)
            fill_radnumeric(page, SEL["item_price"], args.price)
            page.select_option(SEL["item_vat"], args.vat)
            page.wait_for_load_state("networkidle", timeout=30_000)

            # excl. VAT => tax-included toggle must be OFF
            if page.locator(SEL["item_tax_incl"]).is_checked():
                page.locator(SEL["item_tax_toggle"]).click()
                page.wait_for_load_state("networkidle", timeout=30_000)

            page.click(SEL["refresh"])
            page.wait_for_load_state("networkidle", timeout=30_000)

            def safe_fill(selector: str, value: str) -> None:
                if not value:
                    return
                last_err: Exception | None = None
                for _ in range(4):
                    try:
                        page.wait_for_selector(
                            selector, state="visible", timeout=15_000
                        )
                        page.fill(selector, value, timeout=10_000)
                        return
                    except Exception as err:  # noqa: BLE001
                        last_err = err
                        try:
                            page.wait_for_load_state("networkidle", timeout=15_000)
                        except Exception:  # noqa: BLE001
                            pass
                if last_err:
                    raise last_err

            def safe_read(selector: str) -> str:
                try:
                    return page.input_value(selector, timeout=5_000)
                except Exception:  # noqa: BLE001
                    return "<unreadable>"

            page.wait_for_selector(SEL["customer_name"], state="visible", timeout=30_000)
            safe_fill(SEL["customer_name"], args.name)
            safe_fill(SEL["customer_email"], args.email)
            safe_fill(SEL["customer_address"], args.address)
            safe_fill(SEL["customer_city"], args.city)
            safe_fill(SEL["customer_postal"], args.postal)

            print("Filled invoice:")
            print(
                f"  Customer : {safe_read(SEL['customer_name'])!r} "
                f"(Particulier, {args.country})"
            )
            print(
                f"  Line     : {safe_read(SEL['item_desc'])!r} | qty {args.quantity} | "
                f"price {safe_read(SEL['item_price'])!r} | {args.vat}% VAT (excl.)"
            )
            print(f"  Totals   : {read_totals(page)}")

            filled_shot = out_dir / "draft-invoice-filled.png"
            page.screenshot(path=str(filled_shot), full_page=True)

            if args.dry_run:
                print(f"Dry run: nothing saved. Screenshot: {filled_shot}")
                return 0

            button = SEL["send"] if args.send else SEL["save_draft"]
            action = "Verstuur (SENT)" if args.send else "Opslaan als concept (DRAFT)"
            page.click(button)
            page.wait_for_load_state("networkidle", timeout=30_000)

            summary = page.locator(SEL["validation_summary"])
            summary_text = ""
            if summary.count() and summary.is_visible():
                summary_text = summary.inner_text().strip()

            result_shot = out_dir / "draft-invoice-result.png"
            page.screenshot(path=str(result_shot), full_page=True)

            if summary_text:
                print(f"\nValidation blocked the save:\n{summary_text}", file=sys.stderr)
                print(f"Screenshot: {result_shot}", file=sys.stderr)
                return 1

            print(f"\n{action} OK")
            print(f"  Final URL: {page.url}")
            print(f"  Screenshot: {result_shot}")
            return 0
        finally:
            browser.close()


if __name__ == "__main__":
    raise SystemExit(main())
