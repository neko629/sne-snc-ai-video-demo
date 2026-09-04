---
name: trilingual-structure-demo
description: Check the structure of supplied Chinese, pinyin and English three-line blocks. Use for a trilingual text validation demo; this does not generate translations or determine contextual pronunciation.
---

# Trilingual Structure Demo

A reduced adaptation of a trilingual preparation skill. Channel-specific terminology, language style, pronunciation exceptions and review rules are not included.

- Input uses three lines per block: Chinese text (optionally prefixed by a speaker), space-separated pinyin, and English text. Separate blocks with a blank line.
- Run [scripts/check_structure.py](scripts/check_structure.py) before treating a file as structurally complete.
- Return the block numbers with missing fields or inconsistent token counts. Keep supplied text unchanged; ask for the intended content when a correction is ambiguous.
- A count match only establishes structural consistency. Contextual pronunciation and meaning require separate review.

From this skill directory:

```sh
python scripts/check_structure.py --input assets/example.txt
```

The script prints a JSON report and returns a nonzero exit code for invalid input. The fixture is synthetic and contains no episode script or channel naming rules.
