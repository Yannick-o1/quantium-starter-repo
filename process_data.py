"""Create the formatted Pink Morsel sales dataset used by the Dash app."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"product", "price", "quantity", "date", "region"}
INPUT_PATTERN = "daily_sales_data_[0-9].csv"
OUTPUT_FILENAME = "daily_sales_data.csv"


def process_sales_data(
    data_directory: str | Path = Path(__file__).resolve().parent / "data",
    output_file: str | Path | None = None,
) -> pd.DataFrame:
    """Combine the raw CSV files into sales, date and region columns."""
    data_directory = Path(data_directory)
    input_files = sorted(data_directory.glob(INPUT_PATTERN))

    if not input_files:
        raise FileNotFoundError(
            f"No input files matching {INPUT_PATTERN!r} in {data_directory}"
        )

    processed_frames = []

    for input_file in input_files:
        frame = pd.read_csv(input_file)
        missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
        if missing_columns:
            raise ValueError(
                f"{input_file.name} is missing columns: "
                f"{sorted(missing_columns)}"
            )

        is_pink_morsel = (
            frame["product"].astype(str).str.strip().str.casefold()
            == "pink morsel"
        )
        pink_morsels = frame.loc[is_pink_morsel].copy()

        numeric_price = pd.to_numeric(
            pink_morsels["price"]
            .astype(str)
            .str.replace(r"[$,]", "", regex=True),
            errors="raise",
        )
        numeric_quantity = pd.to_numeric(
            pink_morsels["quantity"],
            errors="raise",
        )
        parsed_date = pd.to_datetime(
            pink_morsels["date"],
            errors="raise",
        ).dt.strftime("%Y-%m-%d")

        processed_frames.append(
            pd.DataFrame(
                {
                    "sales": numeric_price * numeric_quantity,
                    "date": parsed_date,
                    "region": pink_morsels["region"]
                    .astype(str)
                    .str.strip(),
                }
            )
        )

    output = pd.concat(processed_frames, ignore_index=True)

    if output.empty:
        raise ValueError("No Pink Morsel transactions were found.")
    if output.isna().any().any():
        raise ValueError("Processed data contains missing values.")

    output_path = (
        Path(output_file)
        if output_file is not None
        else data_directory / OUTPUT_FILENAME
    )
    output.to_csv(output_path, index=False)

    return output


if __name__ == "__main__":
    result = process_sales_data()
    print(
        f"Wrote {len(result):,} Pink Morsel transactions to "
        f"data/{OUTPUT_FILENAME}"
    )
