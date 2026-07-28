# Quantium starter repo
This repo contains everything you need to get started on the program! Good luck!

## Process the Soul Foods sales data

Install the dependencies and run:

```bash
python process_data.py
```

This reads the three raw files in `data/`, keeps Pink Morsel transactions,
calculates `sales = price * quantity`, and writes
`data/daily_sales_data.csv` with the columns `sales`, `date`, and `region`.

Run the automated check with:

```bash
python -m unittest test_process_data.py
```

## Run the Pink Morsel sales visualiser

Create and activate a virtual environment, then install the project
dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Regenerate the processed data if needed and start the Dash app:

```bash
python process_data.py
python app.py
```

Open <http://127.0.0.1:8050> to view the daily Pink Morsel sales line chart.
The chart combines all four regions, sorts the totals by date and marks the
price increase on 15 January 2021. Use the region control to switch between
north, east, south, west and the combined all-region view.

Run all automated checks with:

```bash
python -m unittest
```
