from flask import Flask, render_template, request, send_file
import os
from extractor import extract_financial_data

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        file = request.files["file"]

        if file.filename == "":
            return "No file selected"

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # 🔥 Extract Data
        df = extract_financial_data(filepath)

        # 🔥 Save Excel
        output_path = os.path.join(OUTPUT_FOLDER, "financial_output.xlsx")
        df.to_excel(output_path, index=False)

        # 🔥 Return Excel file for download
        return send_file(output_path, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
