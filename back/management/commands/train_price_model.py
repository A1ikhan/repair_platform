import logging

import joblib
import numpy as np
from django.core.management.base import BaseCommand

from back.services.ml_price_estimator import MODEL_PATH, extract_features, MLPriceEstimator

logger = logging.getLogger(__name__)

MIN_SAMPLES = 20


class Command(BaseCommand):
    help = 'Train RandomForest price prediction model on PriceHistory data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-samples', type=int, default=MIN_SAMPLES,
            help=f'Minimum records required to train (default: {MIN_SAMPLES})'
        )

    def handle(self, *args, **options):
        from back.models.repair_requests_models import PriceHistory

        records = list(
            PriceHistory.objects.filter(final_price__isnull=False)
            .values('device_type', 'problem_description', 'final_price')
        )

        min_samples = options['min_samples']
        if len(records) < min_samples:
            self.stderr.write(
                self.style.ERROR(
                    f'Not enough data: {len(records)} records, need at least {min_samples}.'
                )
            )
            return

        self.stdout.write(f'Training on {len(records)} records...')

        X = np.array([
            extract_features(r['device_type'], r['problem_description'])
            for r in records
        ])
        y = np.array([float(r['final_price']) for r in records])

        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import cross_val_score

        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=8,
            min_samples_leaf=2,
            oob_score=True,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X, y)

        oob_r2 = model.oob_score_
        model._oob_r2 = oob_r2

        # Cross-validation MAE
        cv_scores = cross_val_score(model, X, y, cv=min(5, len(records) // 4),
                                    scoring='neg_mean_absolute_error')
        mae = -cv_scores.mean()

        joblib.dump(model, MODEL_PATH)
        MLPriceEstimator.reload()

        self.stdout.write(self.style.SUCCESS(
            f'\nModel trained and saved to {MODEL_PATH}\n'
            f'  OOB R²  : {oob_r2:.3f}  (1.0 = perfect, >0.7 = good)\n'
            f'  CV MAE  : {mae:,.0f} ₸  (mean absolute error)\n'
            f'  Samples : {len(records)}\n'
        ))

        # Per-device breakdown
        self.stdout.write('Per-device breakdown:')
        from collections import defaultdict
        by_device = defaultdict(list)
        for r in records:
            by_device[r['device_type']].append(float(r['final_price']))

        for device, prices in sorted(by_device.items()):
            avg = sum(prices) / len(prices)
            self.stdout.write(f'  {device:<15} {len(prices):>3} records  avg {avg:>8,.0f} ₸')
