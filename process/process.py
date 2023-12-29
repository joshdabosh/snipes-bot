import squarify

from PIL import Image, ImageDraw, ImageFilter

import json

data = json.load(open("./popularity.json"))

x = 0
y = 0
width = 8000
height = 8000

data = sorted(data, key=lambda x: x[1], reverse=True)

values = [i[1]**1.6 + 1 for i in data]

values = squarify.normalize_sizes(values, width, height)

rects = squarify.padded_squarify(values, x, y, width, height)


canvas = Image.new("RGB", (width, height), (255, 255, 255))

for coords, image_data in zip(rects, data):
    img = Image.open(image_data[0])
    img = img.resize((round(coords["dx"]), round(coords["dy"])))

    canvas.paste(img, (round(coords["x"]), round(coords["y"])))

canvas.save("out.jpg")