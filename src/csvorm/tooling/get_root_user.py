from pathlib import Path

def get_root () -> Path:
  # Ruta del archivo actual
  current_file = Path(__file__).resolve()
  top_project = current_file.parent.parent.parent

  found = False

  # Buscar hacia arriba
  target_file = ".csvorm.toml"
  for parent in [top_project] + list(top_project.parents):
    file_path = parent / target_file
    if file_path.exists():
      found = True
      return file_path.parent

  if not found:
    raise Exception("Debes tener un archivo .csvorm.toml en la raiz del proyecto, mira la documentacion de la herramienta")

  return Path("")
