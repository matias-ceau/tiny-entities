"""Logging configuration for the Tiny Entities simulation."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[Path] = None,
    format_style: str = 'text',
    console_output: bool = True
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file for persistent logs
        format_style: Format style ('text' or 'json')
        console_output: Whether to output to console

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('tiny_entities')
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Create formatters
    if format_style == 'json':
        try:
            from pythonjsonlogger import jsonlogger
            formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(message)s'
            )
        except ImportError:
            # Fallback to text format if pythonjsonlogger not available
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            logger.warning("pythonjsonlogger not available, using text format")
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        try:
            # Ensure directory exists
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            logger.error(f"Failed to create file handler: {e}")

    logger.info(f"Logging initialized at {level} level")
    return logger


class PerformanceLogger:
    """Logger for tracking performance metrics."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('tiny_entities.performance')
        self.metrics = {}

    def record_metric(self, name: str, value: float):
        """Record a performance metric."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

    def log_metrics(self):
        """Log summary statistics for all metrics."""
        if not self.metrics:
            self.logger.info("No performance metrics recorded")
            return

        for name, values in self.metrics.items():
            if not values:
                continue

            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)

            self.logger.info(
                f"Performance: {name} - avg={avg:.4f}s, min={min_val:.4f}s, "
                f"max={max_val:.4f}s, count={len(values)}"
            )

    def clear_metrics(self):
        """Clear all recorded metrics."""
        self.metrics = {}


class TimingContext:
    """Context manager for timing operations."""

    def __init__(self, perf_logger: PerformanceLogger, name: str):
        self.perf_logger = perf_logger
        self.name = name
        self.start_time = None

    def __enter__(self):
        import time
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self.start_time
        self.perf_logger.record_metric(self.name, elapsed)
        return False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f'tiny_entities.{name}')
