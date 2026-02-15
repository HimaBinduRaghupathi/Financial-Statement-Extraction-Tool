import fitz
import pandas as pd
import re
import pytesseract
from PIL import Image
import io

# 🔥 IMPORTANT: Set Tesseract path (Local machine only)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 🔥 Line item mapping
LINE_ITEM_MAP = {
    "Revenue": ["Revenue from operations"],
    "Profit Before Tax": ["Profit before tax"],
    "Net Profit": ["Profit for the year", "Profit after tax"]
}


def extract_financial_data(filepath):

    doc = fitz.open(filepath)
    page = doc[0]

    # Convert PDF page to image for OCR
    pix = page.get_pixmap(dpi=300)
    img_bytes = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_bytes))

    full_text = pytesseract.image_to_string(img)

    # Focus on consolidated section if available
    if "Consolidated" in full_text:
        full_text = full_text.split("Consolidated")[1]

    lines = full_text.split("\n")

    years = ["2025", "2024"]

    extracted = {
        key: [""] * len(years)
        for key in LINE_ITEM_MAP.keys()
    }

    for line in lines:

        for standard_name, keywords in LINE_ITEM_MAP.items():

            for keyword in keywords:

                if keyword.lower() in line.lower():

                    nums = re.findall(r"-?\d[\d,]*\.?\d*", line)

                    filtered = []

                    for num in nums:
                        clean = num.replace(",", "")
                        try:
                            value = float(clean)

                            # Ignore years
                            if 2000 <= value <= 2100:
                                continue

                            # Ignore small values
                            if value < 10000:
                                continue

                            filtered.append(num)

                        except:
                            continue

                    if len(filtered) >= 2:
                        extracted[standard_name] = filtered[:2]

    final_data = []

    for item, values in extracted.items():

        row = {"Line Item": item}

        for i in range(len(years)):
            row[years[i]] = values[i] if i < len(values) else ""

        row["Currency"] = "INR"
        row["Units"] = "Crores"

        # 🔥 Review Needed Logic
        if "" in values:
            row["Review Needed"] = "Yes"
        else:
            row["Review Needed"] = "No"

        final_data.append(row)

    df = pd.DataFrame(final_data)

    cols = ["Line Item"] + years + ["Currency", "Units", "Review Needed"]
    df = df[cols]

    return df
