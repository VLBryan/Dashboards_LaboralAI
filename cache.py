# -------------------------
# Cache / persistencia simple
# -------------------------
def save_df_cache(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)

def load_df_cache(path: str, con_fecha=True) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=False)
    if con_fecha:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df