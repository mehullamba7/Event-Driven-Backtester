import click
from backtester.datasets import make_synthetic_ticks

@click.command()
@click.option('--out', type=click.Path(), required=True)
@click.option('--rows', type=int, default=500000)
def main(out, rows):
    df = make_synthetic_ticks(rows)
    df.to_parquet(out, index=False)
    print(f"Wrote {out} with {len(df):,} rows")

if __name__ == "__main__":
    main()
