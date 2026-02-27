from __future__ import annotations
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data")
OUT_DIR = Path("data")

def list_sheets(xlsx_path: Path) -> list[str]:
    xl = pd.ExcelFile(xlsx_path)
    return xl.sheet_names

def read_sheet(xlsx_path: Path, sheet: str) -> pd.DataFrame:
    df = pd.read_excel(xlsx_path, sheet_name=sheet)
    return df

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    # padroniza nomes de colunas (bem útil)
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("/", "_")
    )
    return df

def coerce_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    xlsx = RAW_DIR / "MVP_FIDC_PDD_Subordinacao_v2.xlsx"
    if not xlsx.exists():
        raise FileNotFoundError(f"Não achei: {xlsx}. Coloque o arquivo em data/")

    print("Abas disponíveis:", list_sheets(xlsx))

    # Leia as abas principais (ajuste se suas abas tiverem nomes diferentes)
    carteira = clean_columns(read_sheet(xlsx, "INPUT_CARTEIRA"))
    regua = clean_columns(read_sheet(xlsx, "REGUA_PDD"))
    params = clean_columns(read_sheet(xlsx, "PARAMETROS"))

    # Tipos (ajuste os nomes conforme suas colunas depois que você olhar o df.head())
    carteira = coerce_numeric(carteira, ["saldo", "dias_atraso"])
    # id_devedor costuma ser texto; deixa como string
    if "id_devedor" in carteira.columns:
        carteira["id_devedor"] = carteira["id_devedor"].astype(str).str.strip()

    # Salvar versões “limpas” em CSV (pra você enxergar e debugar fácil)
    carteira.to_csv(OUT_DIR / "carteira_limpa.csv", index=False, encoding="utf-8-sig")
    regua.to_csv(OUT_DIR / "regua_pdd_limpa.csv", index=False, encoding="utf-8-sig")
    params.to_csv(OUT_DIR / "parametros_limpos.csv", index=False, encoding="utf-8-sig")

    print("OK! Arquivos salvos em data_out/: carteira_limpa.csv, regua_pdd_limpa.csv, parametros_limpos.csv")
    print("\nPreview carteira:")
    print(carteira.head(10))

if __name__ == "__main__":
    main()