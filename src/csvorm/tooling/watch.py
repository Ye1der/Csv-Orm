import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MODELS_DIR = Path("models")
DEBOUNCE_SECONDS = 0.3

class ModelChangeHandler(FileSystemEventHandler):
  def __init__(self):
    self._last_run = 0.0

  def on_any_event(self, event):
    if event.is_directory:
      return

    src_path = str(event.src_path)
    if not src_path.endswith(".py"):
      return

    now = time.time()
    if now - self._last_run < DEBOUNCE_SECONDS:
      return

    self._last_run = now
    print("🔄 Models changed → regenerating types...")
    subprocess.run(["python", "generate_types.py"], check=False)


def main():
  observer = Observer()
  observer.schedule(
    ModelChangeHandler(),
    path=str(MODELS_DIR),
    recursive=True,
  )
  observer.start()

  print("👀 Watching models/ for changes... (Ctrl+C to stop)")

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()

  observer.join()


if __name__ == "__main__":
  main()
