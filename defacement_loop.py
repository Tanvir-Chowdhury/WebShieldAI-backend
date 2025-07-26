
import os
import time
import requests
from io import BytesIO
from PIL import Image
from sqlalchemy.orm import Session
from db import SessionLocal
from models import DefacementLog, Website
from datetime import datetime, timedelta
import numpy as np
import tensorflow as tf
from tensorflow import keras

img_height = 250
img_width = 250
model = keras.models.load_model("ml/defacement_model.h5", compile = False)

class_names = ["clean", "defaced"]

def check(images_path):
    img = keras.preprocessing.image.load_img(
        images_path, target_size=(img_height, img_width)
    )
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch
    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[-1])
    if format(class_names[np.argmax(score)]) == "defaced":
        return 1
    else:
        return 0

def run_defacement_monitor(website_id, website_url):
    while True:
        db = SessionLocal()
        site = db.query(Website).filter(Website.id == website_id).first()
        if not site or not site.defacement_enabled:
            db.close()
            break 
        try:
            print(f"Checking website: {website_url}")
            timestamp = datetime.now()
            screenshot_url = f"https://api.screenshotone.com/take?access_key=LZQpD08KX7gH5g&url={website_url}&format=jpg&block_ads=true&block_cookie_banners=true&block_trackers=true&response_type=by_format&image_quality=80"

            response = requests.get(screenshot_url)
            image = Image.open(BytesIO(response.content))
            image_path = f"screenshot_{website_id}.jpg"
            image.save(image_path)

            result = check(image_path)

            db: Session = SessionLocal()

            log = DefacementLog(
                website_id=website_id,
                prediction="defaced" if result else "clean",
                timestamp=timestamp
            )
            db.add(log)

            cutoff_time = timestamp - timedelta(minutes=60)
            db.query(DefacementLog).filter(
                DefacementLog.website_id == website_id,
                DefacementLog.timestamp < cutoff_time
            ).delete()

            db.commit()
            db.close()

            print(f"Logged defacement check: {result} at {timestamp}")

            os.remove(image_path)
        except Exception as e:
            print(f"Error during defacement check: {e}")

        time.sleep(60)
