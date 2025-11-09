import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# === CONFIGURAÇÕES GERAIS ===
batches_dir = Path("batches_zips")
output_dir = Path("dataset")
train_ratio = 0.8  # 80% treino, 20% validação

# === CONFIGURAÇÕES DO ARQUIVO data.yaml ===
dataset_root_path_for_yaml = "/content/drive/MyDrive/dataset" 
yaml_nc = 2
yaml_names = ['Buy', 'Sell']

# === FUNÇÃO AUXILIAR ===
def extract_date_from_filename(filename: str):
    """
    Extrai a data do formato: <id>-YYYY-MM-DD_<resto_do_nome>.png
    """
    try:
        base = Path(filename).stem
        parts = base.split("-")
        for i, p in enumerate(parts):
            if len(p) == 4 and (i + 2) < len(parts) and len(parts[i+1]) == 2:
                year = p
                month = parts[i+1]
                day = parts[i+2][:2]
                date_part = f"{year}-{month}-{day}"
                return datetime.strptime(date_part, "%Y-%m-%d")
    except (ValueError, IndexError):
        return None
    return None

# === LIMPA E CRIA PASTAS (nova estrutura) ===
for sub in ["images/train", "images/val", "labels/train", "labels/val"]:
    path = output_dir / sub
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)

# Limpa arquivo .yaml antigo, se existir
if (output_dir / "data.yaml").exists():
    os.remove(output_dir / "data.yaml")

# === EXTRAÇÃO DOS ZIPs ===
temp_dir = Path("temp_batches")
if temp_dir.exists():
    shutil.rmtree(temp_dir)
temp_dir.mkdir()

print("📦 Extraindo batches...")
for zip_path in batches_dir.glob("*.zip"):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir / zip_path.stem)

# === COLETA DE PARES (IMG + LABEL) ===
pairs = []
for img_path in temp_dir.rglob("images/*.png"):
    project_dir = img_path.parents[1]
    label_path = project_dir / "labels" / f"{img_path.stem}.txt"
    if label_path.exists():
        date = extract_date_from_filename(img_path.name)
        if date:
            pairs.append((img_path, label_path, date))
        else:
            print(f"⚠️ Aviso: Não foi possível extrair a data de '{img_path.name}'. Arquivo ignorado.")

pairs.sort(key=lambda x: x[2])
print(f"🔍 Total de pares encontrados: {len(pairs)}")

if not pairs:
    print("⚠️ Nenhum par válido encontrado!")
    exit(0)

# === SPLIT TEMPORAL ===
split_idx = int(len(pairs) * train_ratio)
train_pairs = pairs[:split_idx]
val_pairs = pairs[split_idx:]

# === CÓPIA DOS ARQUIVOS PARA AS PASTAS DE TREINO E VALIDAÇÃO ===
def copy_pairs(pairs_list, split_name):
    """Copia pares de imagem e label para as pastas de destino corretas."""
    print(f"🚚 Copiando {len(pairs_list)} arquivos para a pasta '{split_name}'...")
    for img_path, label_path, _ in pairs_list:
        shutil.copy(img_path, output_dir / "images" / split_name / img_path.name)
        shutil.copy(label_path, output_dir / "labels" / split_name / label_path.name)

copy_pairs(train_pairs, "train")
copy_pairs(val_pairs, "val")

# === CÓPIA DE METADADOS ===
for extra_file in ["classes.txt", "notes.json"]:
    for found in temp_dir.rglob(extra_file):
        shutil.copy(found, output_dir / extra_file)
        print(f"📄 Arquivo '{extra_file}' copiado para a pasta do dataset.")
        break

# === GERAÇÃO DO ARQUIVO data.yaml ===
print("📝 Gerando arquivo de configuração data.yaml...")

data_yaml_content = f"""
train: {dataset_root_path_for_yaml}/images/train
val: {dataset_root_path_for_yaml}/images/val

nc: {yaml_nc}
names: {yaml_names}
"""

yaml_path = output_dir / "data.yaml"
with open(yaml_path, "w") as f:
    f.write(data_yaml_content.strip())

print(f"✅ Split temporal feito: {len(train_pairs)} treino / {len(val_pairs)} validação")
print("🎉 Dataset organizado e arquivo data.yaml gerado com sucesso!")
