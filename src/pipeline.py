# Run the whole chain: raw loads -> daily counts -> features -> saved file.
from src.data import PROCESSED, build_daily, load_loads, validate_loads
from src.features import build_features
from src.config import set_seeds
from src.splits import make_splits, save_splits


def main():
    set_seeds()
    loads = validate_loads(load_loads())
    daily = build_daily(loads)
    features = build_features(daily)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = features.join(daily)
    out.to_csv(PROCESSED / "features.csv")
    splits = make_splits(daily)
    save_splits(splits)
    print(f"wrote {len(out)} rows, {out.shape[1]} columns")
    print("splits:", splits)


if __name__ == "__main__":
    main()