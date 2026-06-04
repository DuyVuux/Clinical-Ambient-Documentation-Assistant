# WER Protocol v0.1

## Goal

Current reported baseline: Whisper small trained/fine-tuned on VietMed, WER ~31%.

Target: WER < 20%.

## Metrics

We report:

1. Strict WER
2. Normalized WER
3. Strict CER
4. Normalized CER

## Text normalization

Normalized WER applies:
- lowercase
- punctuation removal
- Unicode NFC
- whitespace normalization
- selected Vietnamese medical number/unit normalization

Examples:
- "năm trăm miligam" → "500 mg"
- "ba mươi bảy độ tám" → "37.8 độ"

## Holdout rule

The ASR holdout set must not be used for training, prompt tuning, decoding tuning, or checkpoint selection.

## Reporting

Every model must be reported on the same manifest.

## Clinical warning

WER is not enough. We also track:
- negation deletion
- medication name error
- dose/unit error
- number error
- medical term error