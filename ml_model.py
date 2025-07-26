import tensorflow as tf
from keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import joblib

tokenizer = Tokenizer(num_words=1000, oov_token="<OOV>")
max_length = 30

model = load_model("ml/sqli_classifier_model.h5")

def prepare_query(query):
    tokenizer.fit_on_texts([query])
    sequences = tokenizer.texts_to_sequences([query])
    padded = pad_sequences(sequences, maxlen=max_length, padding='post') #truncating='post'
    return padded

def predict_query(query):
    processed = prepare_query(query)
    prediction = model.predict(processed)[0][0]
    label = "malicious" if prediction >= 0.8 else "normal"
    return label, float(prediction)

dom_model = joblib.load("ml/dom_model.pkl")
dom_vectorizer = joblib.load("ml/dom_vectorizer.pkl")

def predict_dom_mutation(log):
    transformed = dom_vectorizer.transform([log])
    prediction = dom_model.predict(transformed)[0]
    confidence = dom_model.predict_proba(transformed).max()
    
    label = "suspicious" if prediction == 1 else "normal"
    return label, float(confidence)