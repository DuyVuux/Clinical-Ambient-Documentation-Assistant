import json
from jsonschema import validate, Draft202012Validator
import sys

with open("data/schemas/clinical_fact.schema.json") as f:
    schema = json.load(f)

with open("data/synthetic_data/outpatient_v0_1/SYN_OUT_001/clinical_facts_gold.json") as f:
    facts = json.load(f)

errors = []
validator = Draft202012Validator(schema)
for fact in facts:
    for err in validator.iter_errors(fact):
        errors.append(f"Fact {fact.get('fact_id', 'unknown')}: {err.message}")

if errors:
    print("Errors found:")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print("Validation passed!")
