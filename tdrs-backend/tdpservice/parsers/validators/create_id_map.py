"""Script to generate validator ID map based on the validator files."""

import pathlib

if __name__ == "__main__":
    validator_id_map = dict()
    val_file_path = pathlib.Path(__file__).parent.resolve()
    id = 1
    for i in range(1, 4):
        category = f"category{i}"
        with open(f"{val_file_path}/category{i}.py", "r") as file:
            for line in file.readlines():
                if (line.startswith("def ") and
                        "format_error_context" not in line and
                        "or_priority_validators" not in line and
                        "orValidators" not in line and
                        "ifThenAlso" not in line):
                    name = ""
                    for c in line[4:]:
                        if c == '(':
                            break
                        name += c

                    validator_id_map[id] = (category, name)
                    id += 1

    category = "category4"
    with open(f"{val_file_path}/../case_consistency_validator.py", "r") as file:
        for line in file.readlines():
                line = line.lstrip()
                if (line.startswith("def __validate_") and "section" not in line):
                    name = ""
                    for c in line[4:]:
                        if c == '(':
                            break
                        name += c

                    validator_id_map[id] = (category, name)
                    id += 1

    for key, val in validator_id_map.items():
        print(f"{key}: {val},")
