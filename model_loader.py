import boto3
import tempfile
import joblib
import io
from tensorflow.keras.models import load_model
import streamlit as st

#------------------------Aqi---------------

BUCKET_NAME = "urbanbot-models"
MODEL_KEY = "models/air_lstm_model.h5"
SCALER_KEY = "models/aqi_scaler.pkl"

@st.cache_resource
def load_aqi_model():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"],
        region_name="ap-south-1"
    )

    # -------- MODEL --------
    model_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".h5")  # ✅ FIX
    model_path = model_tmp.name
    model_tmp.close()

    s3.download_file(BUCKET_NAME, MODEL_KEY, model_path)

    model = load_model(model_path, compile=False)

    # -------- SCALER --------
    scaler_obj = s3.get_object(Bucket=BUCKET_NAME, Key=SCALER_KEY)
    scaler = joblib.load(io.BytesIO(scaler_obj["Body"].read()))

    return model, scaler


#----------------Traffic----------------------------

import boto3
import joblib
import io
import streamlit as st
from tensorflow.keras.models import load_model

@st.cache_resource
def load_traffic_model():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"],
        region_name="ap-south-1"
    )

    # Get files from S3
    model_obj = s3.get_object(Bucket=BUCKET_NAME, Key="models/traffic_lstm_model.h5")
    scalerX_obj = s3.get_object(Bucket=BUCKET_NAME, Key="models/traffic_feature_scaler.pkl")
    scalerY_obj = s3.get_object(Bucket=BUCKET_NAME, Key="models/traffic_target_scaler.pkl")

    # Load model 
    with open("temp_model.h5", "wb") as f:
        f.write(model_obj["Body"].read())

    model = load_model("temp_model.h5", compile=False)

    # Load scalers directly
    scaler_X = joblib.load(io.BytesIO(scalerX_obj["Body"].read()))
    scaler_y = joblib.load(io.BytesIO(scalerY_obj["Body"].read()))

    return model, scaler_X, scaler_y

#--------------Road & Accident----------------

from ultralytics import YOLO
@st.cache_resource
def load_yolo_model():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"],
        region_name="ap-south-1"
    )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pt")
    model_path = tmp.name
    tmp.close()

    s3.download_file(BUCKET_NAME, "models/best.pt", model_path)

    model = YOLO(model_path)
    return model

# ---------------- Crowd  ----------------
import torch
import torch.nn as nn
from torchvision import models
import tempfile
import boto3
import streamlit as st

class CrowdNet(nn.Module):
    def __init__(self):
        super().__init__()
        vgg = models.vgg16(weights=None)
        self.frontend = nn.Sequential(*list(vgg.features.children())[:23])
        self.backend = nn.Sequential(
            nn.Conv2d(512,512,3,padding=2,dilation=2),
            nn.ReLU(),
            nn.Conv2d(512,256,3,padding=2,dilation=2),
            nn.ReLU(),
            nn.Conv2d(256,128,3,padding=2,dilation=2),
            nn.ReLU(),
            nn.Conv2d(128,64,3,padding=2,dilation=2),
            nn.ReLU(),
        )
        self.output_layer = nn.Conv2d(64,1,1)

    def forward(self,x):
        x = self.frontend(x)
        x = self.backend(x)
        return self.output_layer(x)


@st.cache_resource
def load_crowd_model():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],   
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"],  
        region_name="ap-south-1"
    )

    tmp = tempfile.NamedTemporaryFile(delete=False)
    model_path = tmp.name
    tmp.close()  

    s3.download_file(BUCKET_NAME, "models/crowd_model.pth", model_path)

    device = torch.device("cpu")

    model = CrowdNet()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    return model

# ---------------- Complaints ----------------
import tempfile
import boto3
import joblib
import streamlit as st

@st.cache_resource
def load_complaint_model():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],   
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"],  
        region_name="ap-south-1"
    )

    # Create temp files and CLOSE them immediately
    model_file = tempfile.NamedTemporaryFile(delete=False)
    model_path = model_file.name
    model_file.close()

    vec_file = tempfile.NamedTemporaryFile(delete=False)
    vec_path = vec_file.name
    vec_file.close()

    le_file = tempfile.NamedTemporaryFile(delete=False)
    le_path = le_file.name
    le_file.close()

    # Download
    s3.download_file(BUCKET_NAME, "models/complaint_ml_model.pkl", model_path)
    s3.download_file(BUCKET_NAME, "models/tfidf_vectorizer.pkl", vec_path)
    s3.download_file(BUCKET_NAME, "models/label_encoder.pkl", le_path)

    # Load
    model = joblib.load(model_path)
    vectorizer = joblib.load(vec_path)
    le = joblib.load(le_path)

    return model, vectorizer, le


