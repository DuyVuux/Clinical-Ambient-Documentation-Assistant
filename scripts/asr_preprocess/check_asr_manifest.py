import json
import os

manifests = [
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_safe_v0_1.jsonl",
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/data/data_lake/silver/asr_manifests/vietmed_dev_preprocessed_selected_safe_v0_1.jsonl"
]

all_pass = True
for m in manifests:
    if not os.path.exists(m):
        print(f"FAIL: {m} not found")
        all_pass = False
        continue
        
    with open(m, 'r') as f:
        for line_num, line in enumerate(f, 1):
            data = json.loads(line)
            if 'sample_id' not in data or 'preprocessed_audio_path' not in data or 'transcript_text' not in data:
                print(f"FAIL: Missing fields in {m} at line {line_num}")
                all_pass = False
                break
            
            audio_path = data['preprocessed_audio_path']
            if not audio_path.startswith('/'):
                audio_path = os.path.join("/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant", audio_path)
            
            if not os.path.exists(audio_path):
                print(f"FAIL: Audio file missing {audio_path} in {m} at line {line_num}")
                all_pass = False
                break

if all_pass:
    print("check_asr_manifest PASS")
