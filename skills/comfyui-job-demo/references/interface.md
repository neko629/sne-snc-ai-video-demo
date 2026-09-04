# Job interface

The workflow is an API node dictionary. `bindings` maps a public parameter to a `node` and `input`; `values` supplies each replacement. Bindings may also map the same value to multiple nodes through a list of targets.

```json
{
  "image": [{"node": "1", "input": "image"}],
  "prompt": [{"node": "2", "input": "text"}],
  "seed": [{"node": "3", "input": "noise_seed"}],
  "output": [{"node": "4", "input": "filename_prefix"}]
}
```

Paths in the command below are relative to this skill folder:

```sh
python scripts/client.py --workflow assets/workflow.mock.json --bindings assets/bindings.demo.json --values assets/values.demo.json
```

The default only prints a plan. A real call requires `--submit --api-base http://127.0.0.1:8188`, your own executable graph and its dependencies. Mock nodes are rejected by the real-submit CLI. No model weights, image upload or remote-file transfer are implemented here.

Transport: `POST /prompt` accepts `prompt` and `client_id`; `GET /history/{prompt_id}` returns status and output metadata. The bundled mock reproduces only the small response subset used by this client and is not a replacement for real integration testing.
