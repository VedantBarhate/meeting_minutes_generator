from flask import Flask, render_template, request, redirect, url_for
from mmg import MeetingMinutesGenerator

app = Flask(__name__)

# Initialize the meeting minutes generator
generator = MeetingMinutesGenerator()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if a file was uploaded
        if "transcript_file" not in request.files:
            return render_template("index.html", error="No file uploaded.")

        file = request.files["transcript_file"]
        if file.filename == "":
            return render_template("index.html", error="No file selected.")

        try:
            # Read the uploaded file
            transcript = file.read().decode("utf-8")
            
            # Generate meeting minutes
            minutes = generator.generate(transcript)
            
            # Pass the result to the result page
            return render_template("result.html", minutes=minutes)
        except Exception as e:
            return render_template("index.html", error=f"Error processing file: {str(e)}")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
