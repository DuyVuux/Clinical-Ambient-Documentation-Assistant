#!/usr/bin/env python3

"""ASR benchmark"""
 
import argparse

import sys

import re

from collections import Counter

from dataclasses import dataclass
 
NEGATION_WORDS: frozenset[str] = frozenset({"không", "chưa", "chẳng", "chả", "đừng", "chớ"})
 
 
def levenshtein(ref: list, hyp: list) -> tuple[int, int, int]:

    """Return (substitutions, deletions, insertions) via dynamic programming."""

    n, m = len(ref), len(hyp)

    # dp[i][j] = (cost, s, d, i_count) for aligning ref[:i] with hyp[:j]

    dp = [[(0, 0, 0, 0)] * (m + 1) for _ in range(n + 1)]
 
    for i in range(1, n + 1):

        dp[i][0] = (i, 0, i, 0)

    for j in range(1, m + 1):

        dp[0][j] = (j, 0, 0, j)
 
    for i in range(1, n + 1):

        for j in range(1, m + 1):

            if ref[i - 1] == hyp[j - 1]:

                cost, s, d, ins = dp[i - 1][j - 1]

                dp[i][j] = (cost, s, d, ins)

            else:

                sub_cost, sub_s, sub_d, sub_i = dp[i - 1][j - 1]

                del_cost, del_s, del_d, del_i = dp[i - 1][j]

                ins_cost, ins_s, ins_d, ins_i = dp[i][j - 1]
 
                best = min(

                    (sub_cost + 1, sub_s + 1, sub_d, sub_i),

                    (del_cost + 1, del_s, del_d + 1, del_i),

                    (ins_cost + 1, ins_s, ins_d, ins_i + 1),

                )

                dp[i][j] = best
 
    _, s, d, ins = dp[n][m]

    return s, d, ins
 
 
@dataclass

class Metrics:

    wer: float

    cer: float

    substitutions: int

    deletions: int

    insertions: int

    ref_words: int

    ref_chars: int

    matched: int

    total_ref: int

    total_hyp: int

    cs_wer: float | None

    cs_substitutions: int

    cs_deletions: int

    cs_insertions: int

    cs_ref_words: int

    n_wer: float | None

    n_substitutions: int

    n_deletions: int

    n_insertions: int

    n_ref_words: int

    negation_miss_rate: float | None

    negation_missed: int

    negation_ref_count: int

    negation_utterances: int
 
 
def is_non_vietnamese(word: str, viet_set: frozenset[str]) -> bool:

    return word not in viet_set
 
 
def load_viet_syllables(path: str) -> frozenset[str]:

    with open(path, encoding="utf-8") as f:

        return frozenset(line.strip().lower() for line in f if line.strip())
 
 
def compute_metrics(

    references: dict[str, str],

    predictions: dict[str, str],

    viet_set: frozenset[str] | None = None,

) -> Metrics:

    total_s = total_d = total_i = 0

    total_ref_words = 0

    char_s = char_d = char_i = 0

    total_ref_chars = 0

    total_cs_s = total_cs_d = total_cs_i = 0

    total_cs_ref_words = 0

    total_n_s = total_n_d = total_n_i = 0

    total_n_ref_words = 0

    total_neg_missed = total_neg_ref = total_neg_utterances = 0

    matched = 0
 
    common_keys = set(references) & set(predictions)
 
    for key in common_keys:

        ref_words = references[key].split()

        hyp_words = predictions[key].split()

        s, d, ins = levenshtein(ref_words, hyp_words)

        total_s += s

        total_d += d

        total_i += ins

        total_ref_words += len(ref_words)
 
        ref_chars = list(references[key].replace(" ", ""))

        hyp_chars = list(predictions[key].replace(" ", ""))

        cs, cd, ci = levenshtein(ref_chars, hyp_chars)

        char_s += cs

        char_d += cd

        char_i += ci

        total_ref_chars += len(ref_chars)
 
        if viet_set is not None:

            ref_cs = [w for w in ref_words if is_non_vietnamese(w, viet_set)]

            hyp_cs = [w for w in hyp_words if is_non_vietnamese(w, viet_set)]

            cs_s, cs_d, cs_i = levenshtein(ref_cs, hyp_cs)

            total_cs_s += cs_s

            total_cs_d += cs_d

            total_cs_i += cs_i

            total_cs_ref_words += len(ref_cs)
 
            ref_n = [w for w in ref_words if not is_non_vietnamese(w, viet_set)]

            hyp_n = [w for w in hyp_words if not is_non_vietnamese(w, viet_set)]

            n_s, n_d, n_i = levenshtein(ref_n, hyp_n)

            total_n_s += n_s

            total_n_d += n_d

            total_n_i += n_i

            total_n_ref_words += len(ref_n)
 
        ref_neg = Counter(w for w in ref_words if w in NEGATION_WORDS)

        hyp_neg = Counter(w for w in hyp_words if w in NEGATION_WORDS)

        utterance_missed = sum(max(0, ref_neg[w] - hyp_neg[w]) for w in ref_neg)

        total_neg_missed += utterance_missed

        total_neg_ref += sum(ref_neg.values())

        if ref_neg:

            total_neg_utterances += 1
 
        matched += 1

    wer =(total_s + total_d + total_i) / total_ref_words if total_ref_words > 0 else 0.0

    cer = (char_s + char_d + char_i) / total_ref_chars if total_ref_chars > 0 else 0.0

    cs_wer = (

        (total_cs_s + total_cs_d + total_cs_i) / total_cs_ref_words

        if viet_set is not None and total_cs_ref_words > 0

        else (0.0 if viet_set is not None else None)

    )

    n_wer = (

        (total_n_s + total_n_d + total_n_i) / total_n_ref_words

        if viet_set is not None and total_n_ref_words > 0

        else (0.0 if viet_set is not None else None)

    )

    negation_miss_rate = total_neg_missed / total_neg_ref if total_neg_ref > 0 else None
 
    return Metrics(

        wer=wer,

        cer=cer,

        substitutions=total_s,

        deletions=total_d,

        insertions=total_i,

        ref_words=total_ref_words,

        ref_chars=total_ref_chars,

        matched=matched,

        total_ref=len(references),

        total_hyp=len(predictions),

        cs_wer=cs_wer,

        cs_substitutions=total_cs_s,

        cs_deletions=total_cs_d,

        cs_insertions=total_cs_i,

        cs_ref_words=total_cs_ref_words,

        n_wer=n_wer,

        n_substitutions=total_n_s,

        n_deletions=total_n_d,

        n_insertions=total_n_i,

        n_ref_words=total_n_ref_words,

        negation_miss_rate=negation_miss_rate,

        negation_missed=total_neg_missed,

        negation_ref_count=total_neg_ref,

        negation_utterances=total_neg_utterances,

    )
 
tone_mapper = {

    'òa': 'oà',

    'óa': 'oá',

    'ỏa': 'oả',

    'õa': 'oã',

    'ọa': 'oạ',

    'òe': 'oè',

    'óe': 'oé',

    'ỏe': 'oẻ',

    'õe': 'oẽ',

    'ọe': 'oẹ',

    'ùy': 'uỳ',

    'úy': 'uý',

    'ủy': 'uỷ',

    'ũy': 'uỹ',

    'ụy': 'uỵ',

}
 
 
def normalize_text(text):

    # Remove language tags like <vi-VN>, <en-US>, etc.

    text = re.sub(r'<[a-zA-Z]{2}-[a-zA-Z]{2,}>', '', text)
 
    # normalize whitespace

    text = re.sub(r'\s+', ' ', text)
 
    # normalize punctuator

    text = re.sub(r'\s[\.|\,|\:|\(|\)|\?|\!|\~|\%]+', ' ', text)

    text = re.sub(r'[\.|\,|\:|\(|\)|\?|\!|\~|\%]+\s', ' ', text)
 
    # normalize tone

    for key in tone_mapper.keys():

        text = text.replace(key, tone_mapper[key])
 
    text = text.strip()

    return text
 
 
def load_file(path: str) -> dict[str, str]:

    """Load tab-separated file: filename<TAB>text, keyed by filename."""

    data = {}

    with open(path, encoding="utf-8") as f:

        for lineno, line in enumerate(f, 1):

            line = line.rstrip("\n")

            if not line.strip():

                continue

            parts = line.split("\t")

            if len(parts) < 2:

                print(f"Warning: {path}:{lineno} has fewer than 2 columns, skipping", file=sys.stderr)

                continue

            filename = parts[0].strip()

            text = normalize_text(parts[1].strip().lower())

            if filename in data:

                print(f"Warning: duplicate filename '{filename}' in {path}:{lineno}", file=sys.stderr)

            data[filename] = text

    return data
 
 
def main():

    parser = argparse.ArgumentParser(description="Benchmark ASR model: compute WER and CER")

    parser.add_argument("--prediction", help="Path to prediction file (filename<TAB>text)")

    parser.add_argument("--transcription", help="Path to reference transcription file (filename<TAB>text)")

    parser.add_argument(

        "--viet-syllables",

        metavar="FILE",

        help="Path to Vietnamese syllable list (one per line). "

             "Download from https://gist.github.com/hieuthi/0f5adb7d3f79e7fb67e0e499004bf558",

    )

    args = parser.parse_args()
 
    references = load_file(args.transcription)

    predictions = load_file(args.prediction)
 
    viet_set = load_viet_syllables(args.viet_syllables) if args.viet_syllables else None

    metrics = compute_metrics(references, predictions, viet_set)
 
    missing_in_pred = set(references) - set(predictions)

    missing_in_ref = set(predictions) - set(references)
 
    print(f"{'='*50}")

    print(f"  ASR Benchmark Results")

    print(f"{'='*50}")

    print(f"  Files matched:        {metrics.matched}")

    print(f"  Reference total:      {metrics.total_ref}")

    print(f"  Prediction total:     {metrics.total_hyp}")

    if missing_in_pred:

        print(f"  Missing in pred:      {len(missing_in_pred)}")

    if missing_in_ref:

        print(f"  Missing in ref:       {len(missing_in_ref)}")

    print(f"{'-'*50}")

    print(f"  WER:                  {metrics.wer * 100:.2f}%")

    print(f"  CER:                  {metrics.cer * 100:.2f}%")

    if metrics.cs_wer is not None:

        print(f"  CS-WER:               {metrics.cs_wer * 100:.2f}%")

        print(f"  N-WER:                {metrics.n_wer * 100:.2f}%")

    else:

        print(f"  CS-WER:               N/A  (use --viet-syllables to enable)")

        print(f"  N-WER:                N/A  (use --viet-syllables to enable)")

    if metrics.negation_miss_rate is not None:

        print(

            f"  Negation miss rate:   {metrics.negation_miss_rate * 100:.2f}%"

            f"  ({metrics.negation_missed} missed / {metrics.negation_ref_count} ref negations,"

            f" {metrics.negation_utterances} utterances)"

        )

    else:

        print(f"  Negation miss rate:   N/A  (no negation words in reference)")

    print(f"{'-'*50}")

    print(f"  Word errors:          {metrics.substitutions + metrics.deletions + metrics.insertions}")

    print(f"    Substitutions:      {metrics.substitutions}")

    print(f"    Deletions:          {metrics.deletions}")

    print(f"    Insertions:         {metrics.insertions}")

    print(f"  Reference words:      {metrics.ref_words}")

    print(f"  Reference chars:      {metrics.ref_chars}")

    if metrics.cs_wer is not None:

        print(f"{'-'*50}")

        print(f"  CS word errors:       {metrics.cs_substitutions + metrics.cs_deletions + metrics.cs_insertions}")

        print(f"    Substitutions:      {metrics.cs_substitutions}")

        print(f"    Deletions:          {metrics.cs_deletions}")

        print(f"    Insertions:         {metrics.cs_insertions}")

        print(f"  CS ref words:         {metrics.cs_ref_words}")

        print(f"  N word errors:        {metrics.n_substitutions + metrics.n_deletions + metrics.n_insertions}")

        print(f"    Substitutions:      {metrics.n_substitutions}")

        print(f"    Deletions:          {metrics.n_deletions}")

        print(f"    Insertions:         {metrics.n_insertions}")

        print(f"  N ref words:          {metrics.n_ref_words}")

    print(f"{'='*50}")
 
 
if __name__ == "__main__":

    main()

 