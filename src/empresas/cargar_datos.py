@st.cache_data(ttl=3600)
def cargar_empresas():

    return load_df_cache(
        "cache/empresas.pkl"
    )


def actualizar_cache_empresas():

    df = build_all(...)

    df.to_pickle(
        "cache/empresas.pkl"
    )

    cargar_empresas.clear()


def build_empresas(db_name: str, mongo_uri: Optional[str] = None, cache_dir: str = "./cache") -> Dict[str, pd.DataFrame]:
    client = get_mongo_client(mongo_uri)
    db = client[db_name]

    # -------------------------
    # df de Métricas generales
    # -------------------------
    Usuarios = pd.DataFrame(list(db.users.find({"isActive": True,"invitationCode": {"$exists": True,"$nin": [None, ""]}}, {"user": 1, "firstName": 1, "lastName": 1, "disponibilidad": 1, "modalidad": 1, "location": 1, "rubros": 1})))
    Cvs = pd.DataFrame(list(db.cvs.find({}, {"user": 1, "profession": 1})))
    #Idioma = pd.DataFrame(list(db.languages.find({}, {"user": 1, "language": 1, "level": 1})))


    Usuarios_Master = Usuarios.merge(Cvs, left_on="_id", right_on="user", how="left")


    # -------------------------
    # Guardar en cache
    # -------------------------
    os.makedirs(cache_dir, exist_ok=True)
    save_df_cache(Usuarios_Master, os.path.join(cache_dir, "Usuarios_Master.csv"))
    
    return Usuarios_Master