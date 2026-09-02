"""AlertManager integration helpers for TDP."""

import logging
from typing import Any, Dict, Optional
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_alert(
    alertname: str,
    summary: str,
    description: str,
    severity: str = "ERROR",
    extra_labels: Optional[Dict[str, str]] = None,
    extra_annotations: Optional[Dict[str, str]] = None,
    timeout: int = 5,
) -> bool:
    """Send an alert to Prometheus AlertManager.

    :param alertname: The name of the alert (e.g. 'RequestParamMismatch')
    :param summary: Brief summary of the alert condition
    :param description: Detailed explanation of the alert condition
    :param severity: Alert severity (e.g. 'ERROR', 'CRITICAL', 'WARNING')
    :param extra_labels: Additional label key-value pairs
    :param extra_annotations: Additional annotation key-value pairs
    :param timeout: Request timeout in seconds
    :return: True if sent successfully, False otherwise
    """
    alertmanager_url = getattr(settings, "ALERTMANAGER_URL", "http://alertmanager:9093")
    if not alertmanager_url:
        logger.debug("ALERTMANAGER_URL not configured; skipping alert dispatch.")
        return False

    api_url = f"{alertmanager_url.rstrip('/')}/api/v2/alerts"

    labels = {
        "alertname": alertname,
        "severity": severity,
        "service": "tdp-backend",
    }
    if extra_labels:
        labels.update(extra_labels)

    annotations = {
        "summary": summary,
        "description": description,
    }
    if extra_annotations:
        annotations.update(extra_annotations)

    payload = [
        {
            "labels": labels,
            "annotations": annotations,
        }
    ]

    try:
        response = requests.post(api_url, json=payload, timeout=timeout)
        response.raise_for_status()
        return True
    except Exception as exc:
        logger.warning(
            "Failed to dispatch alert to AlertManager: %s",
            exc,
            extra={"alertname": alertname, "severity": severity, "api_url": api_url},
        )
        return False

