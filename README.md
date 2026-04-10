# ⚕ MedExtractor

Extracts medications from a HealthWatch Drug Usage Analysis PDF and enriches each with AI-powered clinical and coverage data.

## What It Does

For every drug in your HealthWatch report, it produces:

| Field | Example |
|---|---|
| Drug name + strength | ATORVASTATIN 20 MG |
| DIN / UPC | 02348713 |
| Disease/condition | High cholesterol (hyperlipidemia) |
| Drug class | HMG-CoA reductase inhibitor (Statin) |
| Brand names | Lipitor, Caduet |
| Is generic? | Yes |
| ODB status | Covered |
| ODB notes | General benefit — no LU code required |
| Patient assistance | Pfizer Lipitor Savings Card |
| Copay card available | Yes |
| Ontario benefits | Trillium eligible |

## Setup

1. Copy `.env.example` to `.env` and add your OpenAI key:
```
OPENAI_API_KEY=sk-your-key-here
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
# Full extraction + AI enrichment
python extract.py fast_movers.pdf

# Custom output filename
python extract.py fast_movers.pdf --output my_store_drugs.xlsx

# Extract only (no OpenAI, much faster)
python extract.py fast_movers.pdf --no-enrich
```

## Output

Creates an Excel file with two sheets:
- **Medication Analysis** — all drugs with full enrichment, colour-coded by ODB status
  - 🟢 Green = ODB Covered
  - 🟡 Yellow = Limited Use / conditional
  - 🔴 Red = Not Covered / Unknown
  - ⭐ Star = Copay card available
- **Summary** — count breakdown by ODB status

## Notes

- Works with any HealthWatch Drug Usage Analysis PDF
- Processes ~1 drug every 2 seconds (OpenAI rate limiting)
- For a 100-drug report, expect ~3-4 minutes total
