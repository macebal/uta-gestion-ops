import os
import platform
import subprocess
import tomllib
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path


def format_currency(amount: float | Decimal | str | None) -> str:
    """
    Format a number as currency with space after $ sign.
    Uses commas for thousands separator and dot for decimal separator.

    Examples:
        123456.78 -> "$ 123,456.78"
        1234.5 -> "$ 1,234.50"
        0 -> ""
        None -> ""

    Args:
        amount: The amount to format (can be float, Decimal, string, or None)

    Returns:
        Formatted currency string with space after $ sign
    """
    if not amount or (isinstance(amount, (int, float, Decimal)) and amount == 0):
        return ""

    # Convert string to float if needed
    if isinstance(amount, str):
        clean_str = amount.replace("$", "").replace(",", "").strip()
        try:
            amount = float(clean_str)
        except ValueError:
            return ""

    # Convert to float for formatting
    amount_float = float(amount)

    # Format with 2 decimal places
    amount_str = f"{amount_float:.2f}"

    # Split integer and decimal parts
    integer_part, decimal_part = amount_str.split(".")

    # Add thousands separators (commas) to integer part
    integer_with_commas = ""
    for i, digit in enumerate(reversed(integer_part)):
        if i > 0 and i % 3 == 0:
            integer_with_commas = "," + integer_with_commas
        integer_with_commas = digit + integer_with_commas

    # Format with space after $ and dot for decimal separator
    return f"$ {integer_with_commas}.{decimal_part}"


def parse_currency(currency_str: str) -> Decimal:
    """
    Parse a currency string to Decimal.
    Handles various formats including those with $ sign and commas (thousand separator).

    Args:
        currency_str: String representation of currency

    Returns:
        Decimal value
    """
    if not currency_str:
        return Decimal("0.00")

    # Remove $ sign and commas (thousands separator), keep dot as decimal separator
    clean_str = currency_str.replace("$", "").replace(",", "").strip()

    try:
        return Decimal(clean_str)
    except (ValueError, Exception):
        return Decimal("0.00")


def format_date(date_obj: date | datetime | str | None) -> str:
    """
    Format a date as DD/MM/YYYY.

    Examples:
        date(2024, 11, 1) -> "01/11/2024"
        "2024-11-01" -> "01/11/2024" (if already in correct format, returns as-is)

    Args:
        date_obj: Date object, datetime object, or string to format

    Returns:
        Formatted date string in DD/MM/YYYY format
    """
    if not date_obj:
        return ""

    # If it's already a string, check if it's in the correct format
    if isinstance(date_obj, str):
        # If already in DD/MM/YYYY format, return as-is
        if len(date_obj) == 10 and date_obj[2] == "/" and date_obj[5] == "/":
            return date_obj
        # Otherwise try to parse it
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        except ValueError:
            # If parsing fails, return empty string
            return ""

    # If it's a datetime, extract the date
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()

    return date_obj.strftime("%d/%m/%Y")


def format_check_number(check_number: int | str) -> str:
    """
    Format a check number with zero padding (8 digits).

    Examples:
        123 -> "00000123"
        "456" -> "00000456"

    Args:
        check_number: Check number as integer or string

    Returns:
        Zero-padded check number string (8 digits)
    """
    if isinstance(check_number, str):
        try:
            check_number = int(check_number)
        except ValueError:
            return str(check_number).zfill(8)

    return str(check_number).zfill(8)


def open_file(file_path: str) -> bool:
    """
    Open a file with the system's default application.

    Args:
        file_path: Path to the file to open

    Returns:
        True if the file was opened successfully, False otherwise
    """
    try:
        system = platform.system()

        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":
            subprocess.run(["open", file_path], check=True)
        else:
            subprocess.run(["xdg-open", file_path], check=True)

        return True
    except Exception:
        return False


def get_app_version() -> str:
    """
    Read version from pyproject.toml.

    Returns:
        Version string from pyproject.toml or "Unknown" if not found
    """
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            return pyproject_data.get("project", {}).get("version", "Unknown")
    except Exception:
        return "Unknown"
