import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML  # type: ignore
from weasyprint.text.fonts import FontConfiguration  # type: ignore


def get_template_dir(template_name: str) -> tuple[Path, Path]:
    """Get the template directory and executable directory"""
    if getattr(sys, "frozen", False):
        # If the application is frozen, use the bundle directory
        bundle_dir = Path(sys._MEIPASS)  # type: ignore
        executable_dir = Path(sys.executable).parent
    else:
        # If the application is not frozen, use the current directory
        bundle_dir = Path(__file__).parent.parent.parent
        executable_dir = bundle_dir
    return bundle_dir / "templates" / template_name, executable_dir


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
    template_name = "payment_order"
    template_dir, executable_dir = get_template_dir(template_name)
    template_file = template_dir / f"{template_name}.htm"

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

    pdf_path = executable_dir / output_path
    html_doc.write_pdf(str(pdf_path), font_config=font_config, optimize_images=True)

    return str(pdf_path.absolute())


def create_multiple_payment_orders_pdf(
    payment_orders_data: list[dict[str, str]],
    output_path: str = "payment_orders_batch.pdf",
) -> str:
    """
    Generate a multi-page PDF from multiple payment order templates.

    Args:
        payment_orders_data: List of dictionaries, each containing data for one payment order.
            Each dictionary should have the same keys as expected by create_payment_order_pdf.
        output_path: Path where the PDF will be saved (relative to project root)

    Returns:
        str: Absolute path to the generated PDF file

    Raises:
        FileNotFoundError: If the template file is not found
        Exception: If PDF generation fails
    """
    template_name = "payment_order"
    template_dir, executable_dir = get_template_dir(template_name)
    template_file = template_dir / f"{template_name}.htm"

    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "htm"]),
    )

    template = env.get_template("payment_order.htm")
    font_config = FontConfiguration()

    documents = []
    for order_data in payment_orders_data:
        rendered_html = template.render(**order_data)
        html_doc = HTML(string=rendered_html, base_url=str(template_dir))
        documents.append(html_doc.render(font_config=font_config))

    all_pages = []
    for doc in documents:
        all_pages.extend(doc.pages)

    pdf_path = executable_dir / output_path
    documents[0].copy(all_pages).write_pdf(str(pdf_path))

    return str(pdf_path.absolute())
