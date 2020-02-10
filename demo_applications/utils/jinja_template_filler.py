import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


def main():
    if len(sys.argv) < 4:
        print("Expected arguments: parameter yaml file path, template file path, destination file path [index]", flush=True)
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
        if len(sys.argv) >= 5:
            print(f"index: {sys.argv[4]}")
            config_data["INDEX"] = sys.argv[4]
        result = template.render(config_data)
        file = open(sys.argv[3], "w+")
        file.write(result)
        file.close()
        print("SUCCESS template fill\n", flush=True)


if __name__ == "__main__":
    main()
