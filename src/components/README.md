# UI Components

Standardized, reusable UI components for the UTA Gestión OPS application.

## Components Overview

### Inputs (`inputs.py`)

#### `text_input(label, value="", **kwargs)`
Standard text input field with outlined style.

```python
from src.components import text_input

text_input("Cheque", value="00123456")
text_input("Nombre", classes="flex-1")
```

#### `select_field(options, label, value=None, **kwargs)`
Standard dropdown/select field with outlined style.

```python
from src.components import select_field

select_field(["Sindical", "Otra Cuenta"], label="Cuenta", value="Sindical")
```

#### `select_with_edit(options, label, value=None, on_edit=None, **kwargs)`
Select field with an edit icon button.

```python
from src.components import select_with_edit

def handle_edit():
    print("Edit clicked!")

select_with_edit(
    ["Juan Pérez S.A.", "Otro Proveedor"],
    label="Proveedor",
    value="Juan Pérez S.A.",
    on_edit=handle_edit
)
```

#### `date_input(label, value="", **kwargs)`
Standard date input field.

```python
from src.components import date_input

date_input("Fecha", value="01/01/2025")
```

#### `number_input(label, value="", **kwargs)`
Standard number input field.

```python
from src.components import number_input

number_input("Importe", value="1000")
```

---

### Buttons (`buttons.py`)

#### `primary_button(text, on_click=None, icon=None, **kwargs)`
Primary button with blue background.

```python
from src.components import primary_button

def save_data():
    print("Saving...")

primary_button("Agregar OP", on_click=save_data)
primary_button("Guardar", on_click=save_data, icon="save")
```

#### `secondary_button(text, on_click=None, icon=None, **kwargs)`
Secondary button with gray background.

```python
from src.components import secondary_button

secondary_button("Cancelar", on_click=lambda: print("Cancelled"))
```

#### `small_button(text, on_click=None, icon=None, **kwargs)`
Smaller button for compact spaces.

```python
from src.components import small_button

small_button("Agregar", on_click=add_item)
```

#### `icon_button(icon, on_click=None, color="text-gray-600", **kwargs)`
Icon-only button.

```python
from src.components import icon_button

icon_button("edit", on_click=edit_item, color="text-yellow-500")
icon_button("delete", on_click=delete_item, color="text-red-500")
```

---

### Tables (`tables.py`)

#### `scrollable_table(columns, rows, height="200px", footer_row_html=None, custom_slots=None, **kwargs)`
Standard scrollable table with sticky header and optional footer.

```python
from src.components import scrollable_table

columns = [
    {"name": "id", "label": "ID", "field": "id", "align": "left"},
    {"name": "name", "label": "Nombre", "field": "name", "align": "left"},
]

rows = [
    {"id": "1", "name": "Item 1"},
    {"id": "2", "name": "Item 2"},
]

scrollable_table(columns, rows, height="300px")
```

#### `create_invoice_table(rows, total, on_add_click=None, on_delete_click=None)`
Specialized table for invoices with total row and action buttons.

```python
from src.components import create_invoice_table

rows = [
    {"factura": "01-123", "importe": "$10,000.00", "acciones": "delete"},
    {"factura": "04-567", "importe": "$12,000.00", "acciones": "delete"},
]

create_invoice_table(rows, total="$22,000.00")
```

#### `simple_table(columns, rows, **kwargs)`
Basic table without scrolling or special features.

```python
from src.components import simple_table

simple_table(columns, rows)
```

---

### Menu (`menu.py`)

#### `create_menu()`
Creates the application-wide top menu bar.

```python
from src.components import create_menu

@ui.page("/")
def main_page():
    create_menu()
    # ... rest of page content
```

---

## Usage Example

Here's a complete example of creating a form using these components:

```python
from nicegui import ui
from src.components import (
    text_input,
    select_field,
    date_input,
    primary_button,
    create_menu,
)

@ui.page("/example")
def example_page():
    create_menu()
    
    with ui.column().classes("w-full p-6"):
        with ui.card().classes("w-full max-w-4xl mx-auto p-6"):
            ui.label("Example Form").classes("text-2xl mb-4")
            
            with ui.row().classes("w-full gap-4 mb-4"):
                select_field(
                    ["Option 1", "Option 2"],
                    label="Select One",
                    classes="flex-1"
                )
                date_input("Date", value="01/01/2025", classes="flex-1")
            
            text_input("Name", classes="mb-4")
            
            primary_button("Submit", on_click=lambda: print("Submitted!"))
```

## Customization

All components accept additional keyword arguments that are passed to the underlying NiceGUI elements. You can customize:

- **Classes**: Override default Tailwind classes
- **Props**: Add Quasar props
- **Event handlers**: Add custom event handlers

Example:
```python
text_input(
    "Email",
    classes="flex-1 my-custom-class",
    on_change=lambda e: print(f"Changed to: {e.value}")
)
```

