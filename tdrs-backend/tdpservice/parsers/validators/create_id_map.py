import pathlib
import hashlib
import json

if __name__ == "__main__":
    validator_id_map = dict()
    val_file_path = pathlib.Path(__file__).parent.resolve()
    for i in range(1, 4):
        with open(f"{val_file_path}/category{i}.py", "r") as file:
            for line in file.readlines():
                if (line.startswith("def ") and 
                    "format_error_context" not in line and 
                    "or_priority_validators" not in line and 
                    "orValidators" not in line and 
                    "ifThenAlso" not in line):
                    name = f"cat{i}_"
                    for c in line[4:]:
                        if c == '(':
                            break
                        name += c
                    
                    validator_id_map[name] = hashlib.sha1(name.encode()).hexdigest()
            
    print(json.dumps(validator_id_map, sort_keys=True, indent=4, separators=(',', ': ')))
