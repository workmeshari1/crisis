from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch
import os
import json

app = FastAPI(title="Crisis API")
# ✅ السماح بالوصول من أي مصدر (للتأكد)
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# تحميل الموديل مرة واحدة
model = SentenceTransformer("Omartificial-Intelligence-Space/Arabert-all-nli-triplet-Matryoshka")

def load_data():
    if "GOOGLE_CREDENTIALS" in os.environ:
        creds_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    else:
        raise Exception("❌ GOOGLE_CREDENTIALS not found in environment")

    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    client = gspread.authorize(creds)

    sheet_id = os.getenv("SHEET_ID", "")
    sheet = client.open_by_key(sheet_id)
    ws = sheet.sheet1

    data = ws.get_all_records()
    df = pd.DataFrame(data)
    return df

@app.get("/")
def home():
    return {"message": "🚀 Crisis API running!"}

@app.get("/search")
def search(query: str = Query(..., description="الكلمة أو الوصف للبحث")):
    df = load_data()

    DESC_COL = "وصف الحالة أو الحدث"
    ACTION_COL = "الإجراء"

    if DESC_COL not in df.columns or ACTION_COL not in df.columns:
        return {"error": "❌ الأعمدة ناقصة في Google Sheet"}

    descriptions = df[DESC_COL].fillna("").astype(str).tolist()
    embeddings = model.encode(descriptions, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    cosine_scores = util.pytorch_cos_sim(query_embedding, embeddings)[0]
    top_scores, top_indices = torch.topk(cosine_scores, k=min(5, len(df)))

    results = []
    for score, idx in zip(top_scores, top_indices):
        results.append({
            "الوصف": df.iloc[int(idx.item())][DESC_COL],
            "الإجراء": df.iloc[int(idx.item())][ACTION_COL],
            "درجة_التشابه": float(score)
        })

    return {"query": query, "results": results}
