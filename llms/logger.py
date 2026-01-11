"""
Execution logging system for LLM runs.

Automatically logs prompts, responses, tokens, costs, and latency to JSON files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger


class ExecutionLogger:
    """Manages logging of LLM executions to JSON files."""

    def __init__(self, log_dir: str = "logs"):
        """
        Initialize logger.

        Args:
            log_dir: Directory to store log files (default: "logs")
        """
        self.log_dir = Path(log_dir)
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist."""
        try:
            self.log_dir.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            logger.warning(f"Failed to create log directory {self.log_dir}: {e}")

    def _generate_filename(self, model: str, timestamp: datetime) -> str:
        """
        Generate log filename in format: {model_slug}-{timestamp}.json

        Args:
            model: Model name
            timestamp: Datetime object

        Returns:
            Filename string
        """
        # Clean model name to create slug
        model_slug = (
            model
            .replace('.', '')
            .replace(':', '-')
            .replace('/', '-')
            .replace(' ', '-')
            .lower()
        )

        # Format timestamp: YYYY-MM-DD-HHMMSS
        time_str = timestamp.strftime("%Y-%m-%d-%H%M%S")

        filename = f"{model_slug}-{time_str}.json"

        # Handle potential collisions by adding microseconds
        log_file = self.log_dir / filename
        if log_file.exists():
            micro_str = timestamp.strftime("%f")
            filename = f"{model_slug}-{time_str}-{micro_str}.json"

        return filename

    def log_execution(
        self,
        prompt: dict[str, str | None],
        response: str,
        metadata: dict[str, Any],
        tokens: dict[str, int],
        cost: dict[str, Any],
        latency: float
    ) -> Path | None:
        """
        Log LLM execution to JSON file.

        Args:
            prompt: Dict with 'user' and 'system' prompts
            response: Generated response text
            metadata: Provider metadata (from get_metadata())
            tokens: Token usage dict (input, output, total)
            cost: Cost breakdown dict
            latency: Execution time in milliseconds

        Returns:
            Path to created log file, or None if logging failed
        """
        try:
            timestamp = datetime.now()
            filename = self._generate_filename(metadata["model"], timestamp)
            log_file = self.log_dir / filename

            log_data = {
                "timestamp": timestamp.isoformat(),
                "model": metadata.get("model", "unknown"),
                "provider": metadata.get("provider", "unknown"),
                "prompt": prompt,
                "response": response,
                "tokens": tokens,
                "cost": cost,
                "latency_ms": round(latency, 2),
                "metadata": {
                    "temperature": metadata.get("temperature"),
                    "max_tokens": metadata.get("max_tokens"),
                    "vendor": metadata.get("vendor"),
                    "type": metadata.get("type")
                }
            }

            # Write JSON with pretty formatting
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

            logger.success(f"💾 Logged to: {log_file}")
            return log_file

        except Exception as e:
            logger.error(f"❌ Logging failed: {e}")
            return None

    def add_evaluation_metrics(self, log_file: Path, eval_results: dict[str, Any]):
        """
        Add evaluation metrics to existing log file.

        Args:
            log_file: Path to existing log file
            eval_results: Evaluation results dict

        Raises:
            FileNotFoundError: If log file doesn't exist
            json.JSONDecodeError: If log file is not valid JSON
        """
        try:
            # Read existing log
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Add evaluation section
            data["evaluation"] = eval_results

            # Write updated data
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.success(f"📊 Added evaluation metrics to: {log_file}")

        except FileNotFoundError:
            logger.error(f"❌ Log file not found: {log_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in log file {log_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to add evaluation metrics: {e}")
            raise

    def get_log_stats(self) -> dict[str, Any]:
        """
        Get statistics about logged executions.

        Returns:
            Dict with stats (total logs, total cost, etc.)
        """
        try:
            log_files = list(self.log_dir.glob("*.json"))
            total_logs = len(log_files)

            total_cost = 0.0
            total_tokens = 0
            providers = set()

            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total_cost += data.get("cost", {}).get("total_cost", 0)
                        total_tokens += data.get("tokens", {}).get("total", 0)
                        providers.add(data.get("provider", "unknown"))
                except Exception:
                    continue

            return {
                "total_logs": total_logs,
                "total_cost": round(total_cost, 4),
                "total_tokens": total_tokens,
                "providers_used": sorted(list(providers)),
                "log_directory": str(self.log_dir)
            }

        except Exception as e:
            logger.error(f"❌ Failed to get log stats: {e}")
            return {
                "total_logs": 0,
                "total_cost": 0.0,
                "total_tokens": 0,
                "providers_used": [],
                "log_directory": str(self.log_dir),
                "error": str(e)
            }
