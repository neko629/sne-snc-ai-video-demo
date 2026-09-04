---
name: comfyui-job-demo
description: Prepare parameterized ComfyUI API jobs and inspect their submission and polling lifecycle. Use for a supplied API workflow or the included local mock demo; this skill does not supply a production video model graph.
---

# ComfyUI Job Demo

This is a reduced, adapted version of a private clip-generation skill. It preserves the job interface while omitting production prompts, model settings and asset recipes.

## Inputs and output

- API-format workflow JSON, a mapping of parameter names to node/input fields, and replacement values.
- Output: a planned workflow, or an explicitly requested job ID and returned output metadata.
- Use [references/interface.md](references/interface.md) for the exact input schema and commands.

## Execution

1. Validate every binding before constructing the request. Work on a deep copy; keep the supplied workflow unchanged.
2. Start with a local plan. The included `assets/workflow.mock.json` contains mock-only nodes, not a runnable model graph.
3. When execution against a real endpoint is requested, require the caller's own complete workflow and service configuration. Do not invent missing models, node IDs or credentials.
4. Submit once, retain the returned ID, and poll with a time limit. A failed or uncertain POST must not be blindly resubmitted: it may already have created a job.
5. Report completed, failed and timed-out jobs distinctly. Returned filenames are metadata; check the actual artifact separately before claiming a video was produced.

The included [scripts/client.py](scripts/client.py) implements this contract. The root Demo uses a loopback mock server to exercise it without a ComfyUI service or GPU. Production deployment and model configuration are outside this skill.
