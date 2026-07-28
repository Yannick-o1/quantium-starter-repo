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
