#!/usr/bin/env python3
"""
Run an automated backtest on the improved self-learning model.
Generates a recent-window performance summary and prints it to stdout.
"""

from pprint import pprint

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2


def main() -> None:
    model = ImprovedSelfLearningModelV2()
    report = model.run_automated_backtest(window=60, save_report=True)
    if not report:
        print("No completed games available for automated backtest.")
        return

    print("=== Automated Backtest Summary ===")
    print(f"Window Size: {report.get('window')}")
    print(f"Sample Size: {report.get('sample_size')}")
    print(f"Accuracy: {report.get('accuracy'):.3f}")
    print(f"Upset Rate: {report.get('upset_rate'):.3f}")
    print(f"Brier Score: {report.get('brier'):.3f}")
    print(f"Log Loss: {report.get('log_loss'):.3f}")
    roc_auc = report.get('roc_auc')
    if roc_auc is not None:
        print(f"ROC AUC (Upset Risk): {roc_auc:.3f}")
    precision = report.get('high_risk_precision')
    coverage = report.get('high_risk_coverage')
    if precision is not None and coverage is not None:
        print(
            f"High-Risk Precision (threshold {report['high_risk_threshold']:.2f}): "
            f"{precision:.3f} on {coverage*100:.1f}% of games"
        )
    print("\nContext Buckets:")
    pprint(report.get("context_summary", {}), sort_dicts=True)


if __name__ == "__main__":
    main()

