from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML  # type: ignore
from weasyprint.text.fonts import FontConfiguration  # type: ignore


def create_payment_order_pdf(
    template_data: dict[str, str], output_path: str = "payment_order.pdf"
) -> str:
    """
    Generate a PDF from the payment order template using Jinja2 and WeasyPrint.

    Args:
        template_data: Dictionary containing all the data to populate the template.
            Expected keys:
            - account_name: Name of the account
            - payment_order_id: Order number
            - payment_order_date: Date of the order (DD/MM/YYYY)
            - supplier_name: Name of the supplier
            - invoice_amount: Total invoice amount (formatted as currency)
            - detail: Payment detail description
            - witholding_amount: Withholding amount (formatted as currency)
            - payment_order_total: Net total after retentions (formatted as currency)
            - invoice_number: Invoice number(s)
            - account_number: Bank account number
            - check_number: Check number (zero-padded)
            - issue_date: Issue date (DD/MM/YYYY)
            - due_date: Due date (DD/MM/YYYY)
        output_path: Path where the PDF will be saved (relative to project root)

    Returns:
        str: Absolute path to the generated PDF file

    Raises:
        FileNotFoundError: If the template file is not found
        Exception: If PDF generation fails
    """
    # Get the project root directory (assuming this file is in src/services/)
    project_root = Path(__file__).parent.parent.parent
    template_dir = project_root / "templates" / "payment_order"

    template_file = template_dir / "payment_order.htm"
    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")

    # Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "htm"]),
    )

    # Load and render the template
    template = env.get_template("payment_order.htm")
    rendered_html = template.render(**template_data)

    # Configure font settings for better PDF rendering
    font_config = FontConfiguration()

    html_doc = HTML(string=rendered_html, base_url=str(template_dir))

    pdf_path = project_root / output_path
    html_doc.write_pdf(str(pdf_path), font_config=font_config, optimize_images=True)

    return str(pdf_path.absolute())
