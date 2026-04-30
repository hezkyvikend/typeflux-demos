# Getting Started

Start here if you are new to Typeflux. The notebook keeps every concept inline:

- pydantic input and output schemas
- prompt references and prompt resolution
- a fake structured model provider for deterministic runs
- a tiny workflow built directly in Python
- an optional live OpenAI call once `OPENAI_API_KEY` is present in the root `.env`

## Run

From the repo root:

```bash
cp .env.example .env
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ -e "getting_started[dev]"
jupyter notebook getting_started/getting_started.ipynb
```

The notebook is designed to run top-to-bottom without external services until the final optional live cell.
