import json, click, mlflow, time
from backtester.utils import replay_hash

@click.command()
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--exp-name', type=str, default='exp')
@click.option('--seed', type=int, default=42)
def main(config, exp_name, seed):
    with open(config) as f:
        cfg = json.load(f)
    mlflow.set_experiment(exp_name)
    with mlflow.start_run() as run:
        mlflow.log_params(cfg)
        mlflow.log_param("seed", seed)
        time.sleep(0.2)
        rh = replay_hash(config, cfg.get("data_paths", []))
        mlflow.log_param("replay_hash", rh)
        mlflow.log_metric("net_sharpe", 0.0)
        print("Recorded MLflow run:", run.info.run_id, "replay_hash=", rh)

if __name__ == "__main__":
    main()
