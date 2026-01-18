from pathlib import Path

from csvorm.tooling.get_root_user import get_root

def main():
  import sys

  args = sys.argv[1:]

  if not args:
    print("Usage: csvorm <command>")
    sys.exit(1)

  command = args[0]

  if command == "generate_types":
    from csvorm.tooling.codegen import generate
    generate(get_root())

  if command == "init":
    from csvorm.tooling.init import init_config
    init_config(Path.cwd())

  else:
    print(f"Unknown command: {command}")
    sys.exit(1)

if __name__ == "__main__":
  main()
