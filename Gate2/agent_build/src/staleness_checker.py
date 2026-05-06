"""T-014: Data-stale detection.

The Aurum T-1 batch loads invoices from the previous business day (exported
02:00-04:00 GMT daily). A dispute for a same-day invoice cannot be validity-
assessed until the next batch run.

Per D4 §8 Hard Stop 5: the agent must never assess a dispute without first
checking the invoice date against the batch export date.

Spec source: D4 §4 T-014; D4 §6 ET-004; D4 §8 Hard Stop 5.
"""

from datetime import date


def is_invoice_stale(invoice_dt: date, batch_export_dt: date) -> bool:
    """Return True if the invoice is not yet available in the T-1 batch.

    An invoice is stale (not in T-1) if invoice_dt >= batch_export_dt.
    The T-1 batch contains invoices dated strictly before batch_export_dt.

    If True: the agent must flag the case per T-014, escalate via ET-004
    ("T-1 data unavailable"), and must not proceed to validity assessment.

    Assumption: batch_export_dt is the calendar date the batch file was
    generated (derived from the file modification timestamp or filename).
    The caller is responsible for supplying this value.
    """
    return invoice_dt >= batch_export_dt
