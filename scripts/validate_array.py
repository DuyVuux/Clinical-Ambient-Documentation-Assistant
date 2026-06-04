import json
import jsonschema
import sys

def validate_facts(candidate_file, schema_file):
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    with open(candidate_file, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
        
    if not isinstance(candidates, list):
        print(f"Error: {candidate_file} must contain a JSON array.")
        sys.exit(1)
        
    print(f"Validating {len(candidates)} facts...")
    
    errors = 0
    for i, fact in enumerate(candidates):
        try:
            jsonschema.validate(instance=fact, schema=schema)
            print(f"Fact {i} ({fact.get('fact_id', 'unknown')}): Valid")
        except jsonschema.exceptions.ValidationError as e:
            print(f"Fact {i} ({fact.get('fact_id', 'unknown')}): Invalid")
            print(f"  Error: {e.message}")
            errors += 1
            
    if errors == 0:
        print("\nSUCCESS: All facts are valid according to the schema.")
        sys.exit(0)
    else:
        print(f"\nFAILURE: Found {errors} validation errors.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate_array.py <candidate_file> <schema_file>")
        sys.exit(1)
    
    validate_facts(sys.argv[1], sys.argv[2])
