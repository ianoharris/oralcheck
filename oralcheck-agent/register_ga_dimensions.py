#!/usr/bin/env python3
"""
Register the site's custom event parameters as GA4 custom definitions.

Why this exists: GA4 collects custom event parameters but will not report on
them until they are registered as custom dimensions or metrics, and
**registration is not retroactive**. Every day a parameter goes unregistered is
a day of data that can never be analysed. The site has been sending six of them.

Prerequisites, both one-time and both outside this script:

  1. Enable the Google Analytics Admin API on the Cloud project that owns the
     service account. The Data API is already on; the Admin API is separate.
     https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com

  2. Give the service account **Editor** on the GA4 property. Reading reports
     needs Viewer, creating definitions needs Editor.
     GA4 Admin -> Property access management -> the service account address.

Then:  ./.venv-stats/bin/python register_ga_dimensions.py          # dry run
       ./.venv-stats/bin/python register_ga_dimensions.py --apply  # create

Doing it by hand in the GA4 UI is also fine and takes about a minute per
definition: Admin -> Custom definitions -> Create custom dimension/metric. The
table below is the list to enter.
"""
import os
import sys

from google.oauth2 import service_account
from google.analytics.admin import AnalyticsAdminServiceClient
from google.analytics.admin_v1beta.types import CustomDimension, CustomMetric

# Every custom parameter the site actually sends, from src/app/[locale]/.
#   screener_started   -> question_count
#   screener_completed -> risk_tier, risk_score, has_urgent_symptom
#   email_prompt_shown -> risk_tier
#   find_care_click    -> risk_tier, risk_score, cta_source
DIMENSIONS = [
    ("risk_tier", "Risk tier",
     "low / moderate / elevated / high. The tier shown on the results page."),
    ("has_urgent_symptom", "Urgent symptom reported",
     "true when a symptom lasting 2+ weeks was reported, which overrides the tier."),
    ("cta_source", "CTA source",
     "Which control sent the visitor: results_primary_cta or results_next_step. "
     "Named cta_source rather than source, because GA4 already has a built-in "
     "Source dimension for traffic origin and a custom one by that name collides."),
]

METRICS = [
    ("risk_score", "Risk score", "Raw additive score, 0 to 61.",
     CustomMetric.MeasurementUnit.STANDARD),
    ("question_count", "Question count", "How many questions the screener had at the time.",
     CustomMetric.MeasurementUnit.STANDARD),
]


def main() -> int:
    apply = "--apply" in sys.argv
    key = os.environ.get("GA_SERVICE_ACCOUNT_KEY_PATH", "")
    prop = os.environ.get("GA_PROPERTY_ID", "")
    if not key or not prop:
        print("GA_SERVICE_ACCOUNT_KEY_PATH and GA_PROPERTY_ID must be set (see .env).")
        return 1

    creds = service_account.Credentials.from_service_account_file(
        key, scopes=["https://www.googleapis.com/auth/analytics.edit"])
    client = AnalyticsAdminServiceClient(credentials=creds)
    parent = f"properties/{prop}"

    try:
        have_dims = {d.parameter_name for d in client.list_custom_dimensions(parent=parent)}
        have_mets = {m.parameter_name for m in client.list_custom_metrics(parent=parent)}
    except Exception as exc:
        print(f"Could not read existing definitions: {type(exc).__name__}")
        print(str(exc)[:400])
        print("\nIf this says SERVICE_DISABLED, prerequisite 1 above is not done yet.")
        print("If it says PERMISSION_DENIED on the property, prerequisite 2 is not done yet.")
        return 1

    todo_d = [d for d in DIMENSIONS if d[0] not in have_dims]
    todo_m = [m for m in METRICS if m[0] not in have_mets]

    for name, disp, desc in DIMENSIONS:
        print(f"  dimension  {name:20} {'already registered' if name in have_dims else 'TO CREATE'}")
    for name, disp, desc, _ in METRICS:
        print(f"  metric     {name:20} {'already registered' if name in have_mets else 'TO CREATE'}")

    if not todo_d and not todo_m:
        print("\nEverything is already registered.")
        return 0
    if not apply:
        print(f"\nDry run. {len(todo_d)} dimension(s) and {len(todo_m)} metric(s) would be created.")
        print("Re-run with --apply to create them.")
        return 0

    for name, disp, desc in todo_d:
        client.create_custom_dimension(parent=parent, custom_dimension=CustomDimension(
            parameter_name=name, display_name=disp, description=desc,
            scope=CustomDimension.DimensionScope.EVENT))
        print(f"  created dimension {name}")
    for name, disp, desc, unit in todo_m:
        client.create_custom_metric(parent=parent, custom_metric=CustomMetric(
            parameter_name=name, display_name=disp, description=desc,
            measurement_unit=unit, scope=CustomMetric.MetricScope.EVENT))
        print(f"  created metric {name}")

    print("\nDone. Reporting on these starts from now: GA4 does not backfill.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
