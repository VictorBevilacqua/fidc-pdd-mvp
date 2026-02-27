from __future__ import annotations
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data")          # onde está o xlsx
OUT_DIR = Path("data_out")      # onde salvaremos os CSVs

def list_sheets(xlsx_path: Path) -> list[str]:
    return pd.ExcelFile(xlsx_path).sheet_names

def clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("/", "_")
    )
    # normalizar acentos (somente em colunas)
    df.columns = (
        df.columns
        .str.replace("é", "e").str.replace("ç", "c").str.replace("í", "i")
        .str.replace("ó", "o").str.replace("á", "a").str.replace("â", "a")
        .str.replace("ã", "a").str.replace("ú", "u")
    )
    return df

def read_sheet_smart(xlsx_path: Path, sheet: str, header_key: str = "Data_base", max_scan: int = 30) -> pd.DataFrame:
    """
    Lê as primeiras linhas sem cabeçalho e encontra a linha que contém 'header_key'.
    Depois relê a planilha usando essa linha como header.
    """
    preview = pd.read_excel(xlsx_path, sheet_name=sheet, header=None, nrows=max_scan)

    header_row = None
    for i in range(len(preview)):
        row = preview.iloc[i].astype(str).str.strip().tolist()
        if header_key in row:
            header_row = i
            break

    if header_row is None:
        raise ValueError(f"Não encontrei a linha de cabeçalho com '{header_key}' na aba {sheet}.")

    df = pd.read_excel(xlsx_path, sheet_name=sheet, header=header_row)
    return df

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    xlsx_path = RAW_DIR / "MVP_FIDC_PDD_Subordinacao_v2.xlsx"
    if not xlsx_path.exists():
        raise FileNotFoundError(f"Não achei: {xlsx_path}. Coloque o arquivo em {RAW_DIR}/")

    print("Abas disponíveis:", list_sheets(xlsx_path))

    # ✅ header=1 corrige o problema do "título + Unnamed"
    carteira = read_sheet_smart(xlsx_path, "INPUT_CARTEIRA", header_key="Data_base")
    regua = pd.read_excel(xlsx_path, sheet_name="REGUA_PDD")
    params = pd.read_excel(xlsx_path, sheet_name="PARAMETROS")

    # Limpar nomes de colunas
    carteira = clean_cols(carteira)
    regua = clean_cols(regua)
    params = clean_cols(params)

    # Tipos (ajuste se alguma coluna não existir)
    if "data_base" in carteira.columns:
        carteira["data_base"] = pd.to_datetime(carteira["data_base"], errors="coerce")

    if "dias_atraso" in carteira.columns:
        carteira["dias_atraso"] = pd.to_numeric(carteira["dias_atraso"], errors="coerce").fillna(0).astype(int)

    if "valor_garantia" in carteira.columns:
        carteira["valor_garantia"] = pd.to_numeric(carteira["valor_garantia"], errors="coerce").fillna(0.0)

    if "haircut_garantia" in carteira.columns:
        carteira["haircut_garantia"] = pd.to_numeric(carteira["haircut_garantia"], errors="coerce").fillna(1.0)

    # IDs como string (se existirem)
    for col in ["id_credito", "id_devedor"]:
        if col in carteira.columns:
            carteira[col] = carteira[col].astype(str).str.strip()

    # Salvar saídas
    carteira.to_csv(OUT_DIR / "carteira_canonica.csv", index=False, encoding="utf-8-sig")
    regua.to_csv(OUT_DIR / "regua_pdd_limpa.csv", index=False, encoding="utf-8-sig")
    params.to_csv(OUT_DIR / "parametros_limpos.csv", index=False, encoding="utf-8-sig")

    print("\n✅ Salvos em data_out/: carteira_canonica.csv, regua_pdd_limpa.csv, parametros_limpos.csv")
    print("\nColunas carteira:", carteira.columns.tolist())
    print("\nPreview carteira:")
    print(carteira.head(5)) 
    print("\nDtypes:")
    print(carteira.dtypes)

if __name__ == "__main__":

    
    main()