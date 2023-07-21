# FS (Financni sprava) Processor

## Overview

Use it to generate "DPH" and "Kontrolni hlaseni" reports.
Current version uses [Fakturoid](https://www.fakturoid.cz/) as a data source.
But via implementation of another [processor.py](processor.py), different data source can be used.

## Use

- Create `config.json` file from `config.template.json` file.
- Execute `main.py` and upload generated reports.

## New Data Source

- Implement new data source processor inherited from [processor.py](processor.py) -
  see [fakturoid_processor.py](fakturoid_processor.py) for inspiration.
- Update `config.json` for it.
- Use this new processor in `main.py`.
