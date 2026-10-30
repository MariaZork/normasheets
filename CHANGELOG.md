# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-30

### Added
- YAML sheets with rows of cards, `series.yaml` for shared settings.
- 19 block types: `math`, `equation`, `boxes`, `named_math`, `text`, `label`, `bullets`, `steps`, `checklist`, `chips`, `stats`, `kvgrid`, `table`, `code`, `figure`, `columns`, `tiles`, `spacer`, `html`.
- Inline markup: bold, inline KaTeX, code, sub/superscripts, status tags, colour swatches.
- Custom SVG figures from `figures.py`, with helpers in `normasheets.svg`.
- Bundled KaTeX, Inter and DejaVu Sans Mono for identical output everywhere.
- Layout checks: KaTeX errors, overflow, wrapping, footer collisions, free space, forbidden strings, YAML-eaten backslashes; `--strict` for CI.
- Exports: JPG (2160×2700 at scale 2), PNG and a combined PDF carousel. `pdf_mode: raster` (default) embeds the exact renders so every viewer shows the same colours; `pdf_mode: vector` keeps selectable text.
- `normasheets init` starter project; optional header `logo`.
- Small “made with NoRMA” footer credit, on by default; `credit: false` or custom text in `series.yaml`.
- Example: 9-sheet Navier–Stokes series.
