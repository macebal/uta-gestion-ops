# How to Modify or Recreate Templates

This guide explains the recommended process to modify or recreate the templates for payment orders.

## Step-by-step Instructions

1. **Open the Excel Template**
   - Navigate to the appropriate template folder (e.g., `payment_order/`).
   - Open the Excel file (e.g., `payment_order.xlsx`).

2. **Edit the Template as Needed**
   - Make any necessary changes to the form, text, styles, or layout within Excel.

3. **Export as Web Page**
   - In Excel, choose **File > Save As**.
   - Select **Web Page (.htm, .html)** as the file format.
   - **Important:**
      - In the save dialog, look for options to select **UTF-8 encoding** (ensure the output uses UTF-8).
      - When asked which area to export, **select only the form area** (the minimum rectangular area that encompasses the entire form). This avoids unnecessary content and ensures a clean template.

4. **Rename the Static Assets Folder**
   - After saving, Excel generates a default folder for static assets (images, scripts, etc.).
      - Using a text editor or your operating system, rename this folder to `static` if it’s not already.
      - Ensure all asset references inside the exported `.htm` file also use the name `static`.
   - Update paths inside the `.htm` file if necessary to point to the renamed `static` folder.

5. **Final Checks**
   - Verify that:
      - The exported `.htm` file and `static` folder are correctly named and located within the template folder (e.g., `payment_order/`).
      - All references to images or other assets inside the `.htm` file work as expected.
      - The entire form is visible and functional as a template.

---

**Tip:**
- Always keep a backup of the original Excel and exported files before making changes.
- For other templates, follow the same procedure, adjusting steps as needed for different folder or file names.
