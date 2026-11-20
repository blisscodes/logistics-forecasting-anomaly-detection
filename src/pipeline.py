# Run the whole chain: raw loads -> daily counts -> features -> saved file.
from src.data import PROCESSED, build_daily, load_loads, validate_loads
from src.features import build_features


def main():
    loads = validate_loads(load_loads())
    daily = build_daily(loads)
    features = build_features(daily)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = features.join(daily)
    out.to_csv(PROCESSED / "features.csv")
    print(f"wrote {len(out)} rows, {out.shape[1]} columns")


if __name__ == "__main__":
    main()