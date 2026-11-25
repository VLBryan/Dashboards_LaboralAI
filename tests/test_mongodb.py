"""Pruebas unitarias para utilidades de MongoDB (`mongodb.py`)."""

from bson import ObjectId
import pandas as pd

from mongodb import normalizar_object_ids, safe_merge


def test_normalizar_object_ids_individual_y_listas() -> None:
    oid1 = ObjectId()
    oid2 = ObjectId()
    df = pd.DataFrame(
        {
            "_id": [oid1, oid2],
            "tags": [[oid1, "extra"], [oid2]],
            "nombre": ["A", "B"],
        }
    )

    normalizado = normalizar_object_ids(df)
    assert normalizado["_id"].tolist() == [str(oid1), str(oid2)]
    assert normalizado["tags"].tolist() == [[str(oid1), "extra"], [str(oid2)]]
    assert normalizado["nombre"].tolist() == ["A", "B"]


def test_safe_merge_tolera_dataframes_vacios() -> None:
    left = pd.DataFrame({"_id": ["1", "2"], "nombre": ["Ana", "Luis"]})
    right_vacio = pd.DataFrame()

    res = safe_merge(left, right_vacio, left_on="_id", right_on="user")
    assert res.equals(left)

    res_left_vacio = safe_merge(pd.DataFrame(), left, left_on="_id", right_on="_id")
    assert res_left_vacio.empty
