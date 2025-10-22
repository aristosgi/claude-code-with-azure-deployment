
import logging
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any
from azure.monitor.opentelemetry import configure_azure_monitor
from litellm.integrations.custom_logger import CustomLogger

# -----------------------------
# 1️⃣ Configure Azure Monitor
# -----------------------------
from dotenv import load_dotenv
import sys

load_dotenv()

# Get connection string from environment
connection_string = os.getenv("azure_app_insights_connection_string")

if not connection_string:
    print("❌ ERROR: Azure Application Insights connection string not found in environment variables")
    print("Please set the 'azure_app_insights_connection_string' environment variable")
    sys.exit(1)

try:
    configure_azure_monitor(connection_string=connection_string)
    print("✅ SUCCESS: Azure Monitor configured successfully")
    print("📊 Application Insights telemetry is now active")
except Exception as e:
    print(f"❌ ERROR: Failed to configure Azure Monitor: {e}")
    print("💥 Server shutting down due to telemetry configuration failure")
    sys.exit(1)

# -----------------------------
# 2️⃣ Logger for structured telemetry
# -----------------------------
logger = logging.getLogger("litellm_logger")
logger.setLevel(logging.INFO)

# -----------------------------
# 3️⃣ TokenLogger
# -----------------------------
class TokenLogger(CustomLogger):
    def __init__(self):
        self.model = None

    def log_pre_api_call(self, model: str, _messages: list, _kwargs: Dict[str, Any]) -> None:
        """Log before API call with structured data"""
        self.model = model
        log_dict = {
            "event": "pre_call",
            "model": model,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        logger.info("LLM pre-call event", extra={"custom_dimensions": log_dict})
        print(f"[LOG PRE-CALL] {log_dict}")

    async def async_post_call_streaming_iterator_hook(
        self, request_data, response, user_api_key_dict
    ):
        """Hook used during streaming – captures final token usage"""
        input_tokens = output_tokens = None

        async for chunk in response:
            try:
                chunk_str = chunk.decode("utf-8", errors="ignore")
                if "message_delta" in chunk_str and "usage" in chunk_str:
                    data_json = json.loads(chunk_str.split("data: ")[1])
                    usage = data_json.get("usage", {})
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)
            except Exception as e:
                logger.error("Chunk parsing error", extra={
                    "custom_dimensions": {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
                })

            yield chunk  # Keep streaming alive

        # Log structured usage
        user = os.environ.get("USERNAME", "unknown")
        
        if input_tokens is not None and output_tokens is not None and self.model is not None:
            self._log_to_azure(user, self.model, input_tokens, output_tokens)

    def _log_to_azure(self, user, model, input_tokens, output_tokens):
        """Send structured token usage log to Azure Monitor"""
        log_dict = {
            "user": user,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        logger.info("LLM token usage", extra=log_dict)
        print(f"[LOG SENT TO AZURE] {log_dict}")


# -----------------------------
# 4️⃣ Make instance
# -----------------------------
TokenLogger = TokenLogger()
