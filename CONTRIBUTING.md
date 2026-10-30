# Contributing to NoRMA

Thanks for helping! Bug reports, new block types, themes and example series are all welcome.

## Dev setup

```bash
git clone https://github.com/mariazork/normasheets && cd normasheets
pip install -e .
playwright install chromium
normasheets build examples/navier-stokes --strict   # must pass before a PR
```

## Where things live

| Path | What |
|---|---|
| `normasheets/blocks.py` | block renderers; add one with `@block("name")` |
| `normasheets/inline.py` | inline markup (`**bold**`, `$math$`, tags) |
| `normasheets/render.py` | loading, HTML, layout checks, JPG/PDF export |
| `normasheets/themes/dark.css` | the theme |
| `normasheets/svg.py` | helpers for figure functions |
| `examples/` | example series; also the regression test |

## Adding a block type

1. Write a renderer in `blocks.py` decorated with `@block("your_name")`; give it a one-line docstring (shown by `normasheets blocks`).
2. Style it in `themes/dark.css`.
3. Use it in an example sheet, run `normasheets build examples/navier-stokes --strict`, and look at the output.
4. Document it in the README block table and in `CHANGELOG.md`.

## Pull requests

- One topic per PR, with a before/after screenshot if the output changes.
- Keep the example series passing with `--strict`.
- Show your own series in the README’s *Built with NoRMA* section.
