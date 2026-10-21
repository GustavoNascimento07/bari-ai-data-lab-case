
from pathlib import Path

pasta_laudos = Path("data/raw/laudos")

for arquivo in sorted(pasta_laudos.glob("laudo_*.txt")):
    texto = arquivo.read_text(
        encoding="utf-8",
        errors="replace"
    ).strip()

    print(f"\nArquivo: {arquivo.name}")
    print(f"Quantidade de caracteres: {len(texto)}")

    if texto:
        print("Início do conteúdo:")
        print(texto[:500])
    else:
        print("ATENÇÃO: arquivo vazio")
