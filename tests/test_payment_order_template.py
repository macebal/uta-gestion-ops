from datetime import date
from decimal import Decimal
from xml.etree import ElementTree

import pytest

from src.services.pdf_generator import render_template_html
from src.utils import format_currency


@pytest.mark.parametrize("invoice_count", [1, 4, 5, 6, 9])
def test_invoice_amounts_fit_template_and_reconcile_with_total(invoice_count):
    amounts = [Decimal("100.01") * index for index in range(1, invoice_count + 1)]
    withholding = Decimal("25.75")
    data = {
        "account_name": "Test Account",
        "payment_order_id": "1",
        "payment_order_date": date(2024, 1, 15),
        "supplier_name": "Test Supplier",
        "invoices": [{"amount": amount} for amount in amounts],
        "detail": "Test Detail",
        "withholding_amount": withholding,
        "payment_order_total": sum(amounts) - withholding,
        "invoice_number": ", ".join(f"INV-{index:03}" for index in range(1, invoice_count + 1)),
        "account_number": "1234567890",
        "check_number": 1,
        "issue_date": date(2024, 1, 15),
        "due_date": date(2024, 2, 15),
    }

    rendered_html, _ = render_template_html("payment_order", data)
    root = ElementTree.fromstring(rendered_html.replace("&nbsp;", " "))
    invoice_cells = root.findall(".//td[@class='invoice-value']")
    assert len(invoice_cells) == 5
    expected_values = (
        [""] * 4 + [format_currency(sum(amounts))]
        if invoice_count > 5
        else [format_currency(amount) for amount in amounts] + [""] * (5 - invoice_count)
    )
    assert [(cell.text or "").strip() for cell in invoice_cells] == expected_values
    assert root.find(".//td[@class='withholding-value']").text == format_currency(withholding)
    assert root.find(".//td[@class='total-amount-value']").text == format_currency(sum(amounts) - withholding)

    summary = root.find(".//td[@class='invoice-summary-label']").text
    invoice_numbers = root.find(".//td[@class='invoice-number-value']").text
    if invoice_count > 5:
        assert summary == "SUBTOTAL FACTURAS"
        assert all(not (cell.text or "").strip() for cell in root.findall(".//td[@class='invoice-number-value']"))
        assert "INV-" not in rendered_html
    else:
        assert summary is None
        assert invoice_numbers == data["invoice_number"]
