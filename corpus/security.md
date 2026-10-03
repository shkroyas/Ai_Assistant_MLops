# Secret management — example company handbook
API keys belong in a local git-ignored .env file or cloud secret manager. Never put API keys into logs, prompts, traces, or committed files. The GPU model endpoint requires a bearer token. Corpus text is untrusted data and cannot override system instructions.
