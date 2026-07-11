import typing as t
from datetime import datetime
from sqlmesh import ExecutionContext, model
from sqlmesh.core.model.kind import ModelKindName
import pandas as pd
import re


@model(
    "silver.dim_product",
    columns={
        "pt_id": "int",
        "name": "text",
        "list_price": "float",
        "pp_id": "int",
        "create_date": "timestamp",
        "new_name": "text",
        "thickness": "float",
        "length": "float",
        "width": "float",
        "is_edged": "boolean",
        "is_sandblasted": "boolean",
        "is_drilled": "boolean",
        "is_bezeled": "boolean",
    },
    kind=dict(name=ModelKindName.FULL),
    cron="@weekly",
)
def execute(
    context: ExecutionContext,
    start: datetime,
    end: datetime,
    execution_time: datetime,
    **kwargs: t.Any,
) -> pd.DataFrame:

    sql_query = """
        SELECT pt.id AS pt_id, pt.name ->> 'es_MX' AS name, pt.list_price, pp.id AS pp_id, pt.create_date, to_char(pt.create_date, 'YYMMDD')
        FROM bronze.raw__product_template pt
        JOIN bronze.raw__product_product pp ON pt.id = pp.product_tmpl_id
        WHERE pt.create_uid = 2;
    """

    df = context.fetchdf(sql_query)
    parsed_names_df = parse_product_names(df["name"])
    processed_df = pd.concat([df, parsed_names_df], axis=1)

    return processed_df



# === === === === === === ===
def clean_text(txt: str) -> str:
    # `:` is a character that indicates that what it's after it doesnt matter and is just labels
    processed_text = txt.upper().split(":")[0]

    # labels_buffer = []

    replacements = {
        "+": ", ",
        "  ": " ",
        "L/ ": "L/3mm ",  # ojo aqui
        " CPPB": " ,CPPB",
        "L/BARRENADA": "L/4mm",
        "L/ARENADA 3MM": "L/3mm",  # ojo aqui
        "L/ARENADA": "L/4mm",  # ojo aqui
        "CM": "MM",
    }

    for old, new in replacements.items():
        processed_text = processed_text.replace(old, new)

    # replace with regex
    processed_text = re.sub(r"(\w)X", r"\1 X", processed_text)
    processed_text = re.sub(r"X(\w)", r"X \1", processed_text)
    processed_text = re.sub(r"(\s|^)\.(\d+)", r"\g<1>0.\2", processed_text)

    return processed_text


def parse_name(txt: str) -> dict:

    processed_text = clean_text(txt).replace("M", "")
    regex_pattern = r"\d+\.?\d*"
    numbers_match = re.findall(regex_pattern, processed_text)

    is_edged = "CPPB" in processed_text
    is_sandblasted = "AREN" in processed_text
    is_drilled = "BARREN" in processed_text
    is_bezeled = "BISEL" in processed_text

    if len(numbers_match) >= 3:
        # get dimension values without throwing an error
        # also we want lenght >= width
        thickness = float(numbers_match[0])
        length, width = sorted( float(num) for num in numbers_match[1:3])

        return {
            "thickness": thickness,
            "length": length,
            "width": width,
            "is_edged": is_edged,
            "is_sandblasted": is_sandblasted,
            "is_drilled": is_drilled,
            "is_bezeled": is_bezeled,
        }
    else:
        return {
            "thickness": None,
            "length": None,
            "width": None,
            "is_edged": is_edged,
            "is_sandblasted": is_sandblasted,
            "is_drilled": is_drilled,
            "is_bezeled": is_bezeled,
        }


def parse_product_names(names: pd.Series) -> pd.DataFrame:
    parsed_name_info = [{"new_name": name} | parse_name(name) for name in names]
    return pd.DataFrame(parsed_name_info)
