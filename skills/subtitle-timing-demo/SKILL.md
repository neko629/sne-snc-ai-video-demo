---
name: subtitle-timing-demo
description: Validate a small SRT file and apply an explicit time offset while preserving its text. Use for subtitle timeline demonstrations or supplied SRT offsets, not transcription or translation.
---

# Subtitle Timing Demo

Adapted from a subtitle publishing utility. Only the general timestamp transform is included; channel timelines and release procedures are omitted.

- Require an input SRT, explicit offset in seconds and a distinct output path. Do not infer an offset from private production conventions.
- Use [scripts/timing.py](scripts/timing.py). It checks the simple SRT schema, nonnegative timestamps, positive cue duration and nondecreasing start times.
- Preserve every cue's text. Do not translate or reword it as part of timing adjustment.
- A validation error should identify the cue. Do not silently clamp negative results or overwrite the input file.
- This is structural validation; it does not establish speech synchronization or translation quality.

From this skill directory:

```sh
python scripts/timing.py --input assets/example.srt --output shifted.srt --offset 0.75
```

The sample text and offset are generic demonstration values. No external service is called.
