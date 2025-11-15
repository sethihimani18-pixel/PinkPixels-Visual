from flask import Flask, request, jsonify, send_file, render_template
import os
from PIL import Image
import numpy as np
import difflib

#creating an instance in flask

vde = Flask(__name__)
UPLOAD_FOLDER = "uploads"
DIFF_FOLDER = "diff"

#making directories if not exist

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DIFF_FOLDER, exist_ok=True)

#comparing text files

def compare_text(file1, file2):
    with open(file1, "r") as f1:
        lines1 = f1.readlines()

    with open(file2, "r") as f2:
        lines2 = f2.readlines()

    diff = difflib.unified_diff(lines1, lines2, fromfile="file1", tofile="file2")

    diff_text = "".join(diff)
    return diff_text

#comparing image files
def compare_images(file1, file2):
    img1 = Image.open(file1).convert("RGB")
    img2 = Image.open(file2).convert("RGB")

#resize to match shapes if needed
    img2 = img2.resize(img1.size)

    arr1 = np.array(img1)
    arr2 = np.array(img2)

#pixel difference
    diff = np.abs(arr1 - arr2)

#highlight differences
    diff_img = Image.fromarray(diff.astype(np.uint8))

    output_path = os.path.join(DIFF_FOLDER, "difference.png")
    diff_img.save(output_path)

    return output_path

#route for comparing files

@vde.route("/compare", methods=["POST"])
def compare():
    file1 = request.files["file1"]
    file2 = request.files["file2"]

    path1 = os.path.join(UPLOAD_FOLDER, file1.filename)
    path2 = os.path.join(UPLOAD_FOLDER, file2.filename)

    file1.save(path1)
    file2.save(path2)

    if file1.filename.endswith(".txt") or file2.filename.endswith(".txt"):
        diff_text = compare_text(path1, path2)
        return jsonify({"result": diff_text})

    else:
        diff_image = compare_images(path1, path2)
        return send_file(diff_image, mimetype="image/png")
    
#home route

@vde.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    vde.run(debug=True)
