import sys

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
import yaml


def main():
    if len(sys.argv) < 4:
        print("Expected arguments: parameter yaml file path, target file path, destination file path")
    else:
        print("\nSTART Jinja template fill")
        print(f"yaml file:   {sys.argv[1]}\ntarget file: {sys.argv[2]}\ndest file:   {sys.argv[3]}")
        target_path = Path(sys.argv[2])
        environment = Environment(
            loader=FileSystemLoader(str(target_path.parent)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = environment.get_template(target_path.name)
        config_data = yaml.load(open(sys.argv[1]), Loader=yaml.FullLoader)
        result = template.render(config_data)
        file = open(sys.argv[3], "w+")
        file.write(result)
        file.close()
        print("SUCCESS template fill\n")


if __name__ == "__main__":
    main()
