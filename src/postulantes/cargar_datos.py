# src/cargar_datos.py
"""
Carga de datos del módulo de Postulantes/Candidatos.

Adaptado a la plantilla: sin archivos físicos de caché, usando
@st.cache_data para mantener el DataFrame en RAM.
"""

import os
from typing import List, Dict, Optional
import pandas as pd
import streamlit as st
from pymongo import MongoClient

try:
    from bson import ObjectId
except Exception:
    ObjectId = None


def get_mongo_client(uri: Optional[str] = None) -> MongoClient:
    uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
    return MongoClient(uri)


def get_collection_df(client: MongoClient, db_name: str, coll_name: str) -> pd.DataFrame:
    db = client[db_name]
    cursor = db[coll_name].find()
    return pd.DataFrame(list(cursor))


def load_collections(client: MongoClient, db_name: str, collections: List[str]) -> Dict[str, pd.DataFrame]:
    out = {}
    for c in collections:
        try:
            out[c] = get_collection_df(client, db_name, c)
        except Exception as e:
            print(f"Warning: no se pudo cargar {c}: {e}")
            out[c] = pd.DataFrame()
    return out


@st.cache_data(ttl=600, show_spinner="Cargando candidatos desde MongoDB...")
def build_all(db_name: str, mongo_uri: Optional[str] = None, cache_dir: str = "./cache") -> pd.DataFrame:
    client = get_mongo_client(mongo_uri)
    db = client[db_name]

    Usuarios = pd.DataFrame(list(db.users.find(
        {"isActive": True, "invitationCode": {"$exists": True, "$nin": [None, ""]}},
        {"user": 1, "firstName": 1, "lastName": 1, "disponibilidad": 1,
         "modalidad": 1, "location": 1, "rubros": 1}
    )))
    Cvs = pd.DataFrame(list(db.cvs.find({}, {"user": 1, "profession": 1})))

    Usuarios_Master = Usuarios.merge(Cvs, left_on="_id", right_on="user", how="left")

    client.close()
    return Usuarios_Master
