"""Middleware request interceptor for parameter mismatches."""

import json
import logging
from typing import Any, Dict

from tdpservice.alerts.alertmanager import send_alert
from tdpservice.core.models import BaseLog

logger = logging.getLogger(__name__)


class RequestParamMismatchMiddleware:
    """Intercept PUT/POST/PATCH requests to detect, log, and alert on parameter mismatches."""

    INTERCEPTED_METHODS = ("POST", "PUT", "PATCH")

    def __init__(self, get_response):
        """Initialize middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Inspect request parameters and continue downstream execution."""
        try:
            self._inspect_request_parameters(request)
        except Exception as exc:
            logger.warning("Failed inspecting request parameters for mismatch: %s", exc)

        return self.get_response(request)

    def _inspect_request_parameters(self, request):
        """Check for parameter mismatches between query string and body payload."""
        if request.method not in self.INTERCEPTED_METHODS:
            return

        if not request.GET:
            return

        body_data = self._extract_body_params(request)
        if not body_data:
            return

        mismatches = self._find_mismatches(request.GET, body_data)
        if not mismatches:
            return

        self._handle_mismatch(request, mismatches, body_data)

    def _extract_body_params(self, request) -> Dict[str, Any]:
        """Extract body parameters from json or form data safely."""
        content_type = request.content_type or ""

        if "application/json" in content_type:
            try:
                body = request.body
                if body:
                    data = json.loads(body.decode("utf-8"))
                    if isinstance(data, dict):
                        return data
            except Exception as exc:
                logger.debug("Unable to parse JSON body for param check: %s", exc)
                return {}

        if request.POST:
            return request.POST

        return {}

    def _find_mismatches(self, query_dict, body_dict) -> Dict[str, Dict[str, str]]:
        """Compare overlapping keys in query and body dictionaries."""
        mismatches = {}
        overlapping_keys = set(query_dict.keys()) & set(body_dict.keys())

        for key in overlapping_keys:
            query_val = query_dict.get(key)
            body_val = body_dict.get(key)

            if isinstance(body_val, list) and len(body_val) == 1:
                body_val = body_val[0]

            if str(query_val).strip() != str(body_val).strip():
                mismatches[key] = {
                    "query": str(query_val),
                    "body": str(body_val),
                }

        return mismatches

    def _is_file_upload_request(self, request, body_data) -> bool:
        """Return True if this request is a file upload submission."""
        path = getattr(request, "path_info", request.path) or ""
        if "/data_files" in path:
            return True
        if getattr(request, "FILES", None) and len(request.FILES) > 0:
            return True
        if body_data and "file" in body_data:
            return True
        return False

    def _handle_mismatch(self, request, mismatches, body_data):
        """Log mismatch details and alert admins if criteria are met."""
        path = getattr(request, "path_info", request.path)
        is_file_upload = self._is_file_upload_request(request, body_data)
        user = getattr(request, "user", None)
        actor = user if getattr(user, "is_authenticated", False) else None
        username = getattr(actor, "username", "anonymous") if actor else "anonymous"

        metadata = {
            "path": path,
            "method": request.method,
            "mismatches": mismatches,
            "query_params": {
                k: request.GET.getlist(k) if len(request.GET.getlist(k)) > 1 else request.GET.get(k)
                for k in request.GET
            },
            "is_file_upload": is_file_upload,
        }
        if actor:
            metadata["user_id"] = actor.id
            metadata["username"] = username

        logger.warning(
            "Request parameter mismatch on %s %s: %s",
            request.method,
            path,
            mismatches,
            extra=metadata,
        )

        try:
            BaseLog.objects.create_for_object(
                obj=actor,
                event_type="request_param_mismatch",
                note=f"Request parameter mismatch on {request.method} {path}",
                metadata=metadata,
                actor=actor,
                source="middleware",
            )
        except Exception as exc:
            logger.warning("Failed to save BaseLog for request param mismatch: %s", exc)

        if is_file_upload:
            try:
                send_alert(
                    alertname="RequestParamMismatch",
                    summary=f"File upload request parameter mismatch on {path}",
                    description=(
                        f"User '{username}' submitted a file upload on {request.method} {path} "
                        f"with mismatched parameters: {mismatches}"
                    ),
                    severity="ERROR",
                    extra_labels={
                        "endpoint": path,
                        "method": request.method,
                        "mismatch_type": "file_upload",
                    },
                    extra_annotations={
                        "mismatches": json.dumps(mismatches),
                    },
                )
            except Exception as exc:
                logger.warning("Failed to dispatch alert for request param mismatch: %s", exc)
