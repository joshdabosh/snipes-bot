import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import json
import os, sys

from urllib.parse import urlparse

import requests

import tqdm

if len(sys.argv) != 2:
    print("Usage: python dump.py <server id>")
    exit(1)

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

coll = db.collection(sys.argv[1])

images = []

for doc in coll.stream():
    dat = doc.to_dict()
    images.append([dat["image_link"], len(dat["upvotes"])])

ctr = 0

pathmapping = []

for image_url, popularity in tqdm.tqdm(images):
    image_data = requests.get(image_url).content

    fname = os.path.basename(urlparse(image_url).path)

    if fname.endswith(".mov") or len(image_data) == 0:
        continue

    fname = os.path.join("images", str(ctr) + "_" + fname)

    with open(fname, "wb") as f:
        f.write(image_data)

    pathmapping.append([fname, popularity])

    ctr += 1

with open("popularity.json", "w") as f:
    f.write(json.dumps(pathmapping))