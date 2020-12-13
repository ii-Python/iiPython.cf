# Modules
import io
from app import app

from os import listdir
from requests import get

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from PIL import Image, ImageDraw, ImageFont
from flask import make_response, request, abort, render_template

# Routes
@app.route("/text")
def genImage():

    query = request.args.get("text", "None")
    font = request.args.get("font", "regular")

    try:
        r = int(request.args.get("r", 255))
        g = int(request.args.get("g", 255))
        b = int(request.args.get("b", 255))

    except ValueError:
        return "Invalid RGB value.", 400

    for file in listdir("assets/fonts"):
        if font in file.lower():
            font = file

    if font not in listdir("assets/fonts"):
        return "Invalid font.", 404

    fontsize = 45

    if len(query) > 60:

        excess = len(query) - 60

        if excess > 300:
            return "Payload too large, must be at most 360 characters.", 400

        fontsize -= excess

    # Image drawing
    image = Image.new("RGBA", (1366, 70), color = (0, 0, 0, 0))
    d = ImageDraw.Draw(image)
    d.text((10, 10), query, font = ImageFont.truetype(f"assets/fonts/{font}", fontsize), fill = (r, g, b))

    # Image saving
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format = "PNG")

    # Returning
    response = make_response(imgByteArr.getvalue())
    response.headers.set("Content-Type", "image/png")

    return response, 200

@app.route("/badge")
def genBadge():

    title = request.args.get("title")
    description = request.args.get("description")
    color = request.args.get("color", "000000")

    # Color hex removing
    if color[0] == "#":
        color = color[1:]

    # Create our bytes array
    imgByteArr = io.BytesIO()
    render = svg2rlg(io.BytesIO(get(f"https://img.shields.io/badge/{title}-{description}-{color}.svg", allow_redirects = True).content))

    # Saving to temp file
    renderPM.drawToFile(render, imgByteArr, fmt = "PNG")

    # Returning badge
    response = make_response(imgByteArr.getvalue())
    response.headers.set("Content-Type", "image/png")

    return response, 200

@app.route("/badge/generate", methods = ["GET"])
def badgePage():

    return render_template("generators/badge.html"), 200

@app.route("/embed", methods = ["GET"])
def generateEmbed():

    return render_template("api/embed.html"), 200

@app.route("/embed/generate", methods = ["GET"])
def embedPage():

    return render_template("generators/embed.html"), 200

@app.route("/oembed", methods = ["GET"])
def generateOEmbed():

    author = request.args.get("author")

    if not author:
        return abort(400)

    response = '{{"type":"photo","author_name":"{}"}}'
    return response.format(author), 200
