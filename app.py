from flask import Flask, render_template, request, send_file, jsonify, redirect, after_this_request
import os
import tempfile
from werkzeug.utils import secure_filename
from services.extract_text_from_document import extract_text_from_document
from services.generator import (
    generate_text_answer,
    generate_code_solution,
    generate_word_solution,
    _detect_file_extension_requirement
)

# =========================================
# ⚙️ APP CONFIGURATION
# =========================================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "doc", "txt",  # Documents
    "cpp", "c", "h", "hpp",  # C/C++
    "py", "pyw",  # Python
    "java", "class",  # Java
    "js", "jsx", "ts", "tsx",  # JavaScript/TypeScript
    "html", "htm", "css",  # Web
    "cs", "vb",  # C#, VB
    "php", "rb", "go", "rs",  # Other languages
    "sql", "json", "xml", "yaml", "yml"  # Data files
}


# =========================================
# ✅ HELPER FUNCTIONS
# =========================================
def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# =========================================
# 🌍 ROUTES
# =========================================
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/assignment-generator")
def assignment_generator():
    return render_template("assignment_generator.html")


@app.route("/generate-gdb", methods=["GET", "POST"])
def gdb_generator():
    """Handle Q&A generation requests."""
    if request.method == "GET":
        return render_template("gdb_generator.html")

    try:
        gdb_text = request.form.get("gdb_text", "").strip()
        if not gdb_text:
            return jsonify({"success": False, "error": "No question provided"}), 400

        answer = generate_text_answer(gdb_text)
        return jsonify({"success": True, "content": answer})

    except Exception as e:
        print(f"⚠️ GDB generation error: {e}")
        return jsonify({"success": False, "error": f"Error generating answer: {str(e)}"}), 500




@app.route("/blog")
def blog():
    return render_template("blog.html")


@app.route("/blog/<post_slug>")
def blog_post(post_slug):
    valid_posts = [
        "understanding-pointers-cpp",
        "python-data-structures-guide",
        "debugging-techniques-students",
        "object-oriented-programming-java",
        "mastering-algorithms-data-structures",
        "web-development-html-css-javascript",
        "version-control-git-github",
        "database-fundamentals-sql",
        "machine-learning-beginners",
        "cybersecurity-best-practices",
        "spring-boot-rest-api-beginners"
    ]

    if post_slug not in valid_posts:
        return redirect("/blog")
    return render_template(f"blog_posts/{post_slug}.html")


# =========================================
# 📤 FILE UPLOAD LOGIC
# =========================================
@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file uploads and assignment generation."""
    temp_files = []
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file part"}), 400

        files = request.files.getlist("file")
        if not files or all(not f.filename for f in files):
            return jsonify({"success": False, "error": "No files selected"}), 400

        combined_text = ""
        for file in files:
            if not allowed_file(file.filename):
                return jsonify({"success": False, "error": f"Invalid file type: {secure_filename(file.filename)}"}), 400

            with tempfile.NamedTemporaryFile(delete=False, dir=tempfile.gettempdir(), suffix=os.path.splitext(file.filename)[1]) as temp_upload:
                file.save(temp_upload.name)
                temp_files.append(temp_upload.name)

            extracted_text = extract_text_from_document(temp_upload.name)
            if extracted_text:
                combined_text += f"\n\n=== File: {secure_filename(file.filename)} ===\n{extracted_text}"

        if not combined_text.strip():
            return jsonify({"success": False, "error": "No readable text found in uploaded files."}), 400

        detected_extension = _detect_file_extension_requirement(combined_text)
        with tempfile.NamedTemporaryFile(delete=False, dir=tempfile.gettempdir(), suffix=f".{detected_extension}") as temp_output:
            output_path = temp_output.name
            temp_files.append(output_path)

        # Generate the assignment output
        if detected_extension in ["cpp", "py", "java", "c", "js", "html", "cs", "php", "rb", "go", "rs"]:
            generate_code_solution(combined_text, language=detected_extension, filename=output_path)
            file_type = "code"
        else:
            generate_word_solution(combined_text, filename=output_path)
            detected_extension = "docx"
            file_type = "document"

        # Prepare final file for download
        final_temp = tempfile.NamedTemporaryFile(delete=False, dir=tempfile.gettempdir(), suffix=f".{detected_extension}")
        with open(output_path, "rb") as src:
            final_temp.write(src.read())
        final_temp.close()

        @after_this_request
        def cleanup(response):
            for temp_path in temp_files + [final_temp.name]:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception:
                    pass
            return response

        print(f"✅ Successfully generated {file_type} solution: {final_temp.name}")
        return send_file(final_temp.name, as_attachment=True, download_name=f"Solution.{detected_extension}")

    except Exception as e:
        print(f"❌ Upload processing error: {e}")
        for t in temp_files:
            try:
                if os.path.exists(t):
                    os.remove(t)
            except Exception:
                pass
        return jsonify({"success": False, "error": f"Error processing assignment: {str(e)}"}), 500


# =========================================
# ⚠️ ERROR HANDLERS & SECURITY HEADERS
# =========================================
@app.errorhandler(413)
def too_large(error):
    return jsonify({"success": False, "error": "File too large. Please upload files smaller than 50MB."}), 413


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# =========================================
# 🚀 APP ENTRY POINT
# =========================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # DigitalOcean requires port 8080
    print(f"🚀 Starting Flask on 0.0.0.0:{port}")
    app.run(debug=False, host="0.0.0.0", port=port)
