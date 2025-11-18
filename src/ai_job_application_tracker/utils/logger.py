"""
Logging configuration for Job Application Tracker.

This module sets up logging for the entire application.
It creates both console output (terminal) and file output (logs/job_tracker.log).

Usage:
    from utils.logger import setup_logger

    logger = setup_logger()
    logger.info("Application started")
    logger.error("Something went wrong!")
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "job_tracker", level: str = "INFO") -> logging.Logger:
    """
    Set up logger with console and file handlers.

    This creates a logger that:
    1. Prints to console (terminal) with timestamps
    2. Saves to logs/job_tracker.log with detailed info
    3. Supports different log levels (DEBUG, INFO, WARNING, ERROR)

    Args:
        name: Logger name (default: "job_tracker")
        level: Logging level - DEBUG, INFO, WARNING, ERROR (default: "INFO")

    Returns:
        Configured logger instance

    Example:
        logger = setup_logger()
        logger.info("Starting email fetch")
        logger.error("Failed to connect to Gmail")

    Log Levels:
        DEBUG - Detailed information, typically for debugging
        INFO - General information about what's happening
        WARNING - Something unexpected but not critical
        ERROR - Serious problem, something failed
    """

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Avoid duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # ========================================
    # Console Handler (Terminal Output)
    # ========================================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Format for console: Simple and clean
    # Example: "14:30:15 - INFO - Fetched 25 emails from Gmail"
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # ========================================
    # File Handler (Save to logs/job_tracker.log)
    # ========================================
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)  # Create logs directory if it doesn't exist

    log_file = log_dir / "job_tracker.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # Save everything to file

    # Format for file: More detailed with module name
    # Example: "2025-11-18 14:30:15 - job_tracker - INFO - Fetched 25 emails from Gmail"
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Log that logging is set up
    logger.debug(f"Logger initialized: {name} at level {level}")
    logger.debug(f"Log file: {log_file.absolute()}")

    return logger


def get_logger(name: str = "job_tracker") -> logging.Logger:
    """
    Get an existing logger or create a new one.

    This is a convenience function for getting the logger in other modules.

    Args:
        name: Logger name

    Returns:
        Logger instance

    Example:
        from utils.logger import get_logger

        logger = get_logger()
        logger.info("Email fetching started")
    """
    return logging.getLogger(name)


# Example usage and testing
if __name__ == "__main__":
    """
    Test the logger by creating various log messages.

    Run this file directly to see logging in action:
        python utils/logger.py
    """

    print("=" * 60)
    print("TESTING LOGGER")
    print("=" * 60)
    print()

    # Create logger
    logger = setup_logger(level="DEBUG")

    # Test different log levels
    logger.debug("🔍 This is a DEBUG message - detailed info for developers")
    logger.info("ℹ️ This is an INFO message - general information")
    logger.warning("⚠️ This is a WARNING message - something unexpected")
    logger.error("❌ This is an ERROR message - something failed!")

    print()
    print("-" * 60)
    print("Simulating application flow:")
    print("-" * 60)

    # Simulate real application logging
    logger.info("📧 Application started")
    logger.info("📂 Loading configuration from config/config.yaml")
    logger.info("   ✓ Loaded 3 email accounts")
    logger.info("   ✓ LLM provider: anthropic")

    logger.info("")
    logger.info("🔐 Authenticating email accounts...")
    logger.info("   📧 Gmail: hajiyev.shamkhal@gmail.com")
    logger.debug("      Token file: config/tokens/gmail_personal.json")
    logger.info("      ✅ Token loaded successfully")

    logger.info("")
    logger.info("📥 Fetching emails from last 30 days...")
    logger.info("   Found 25 emails from Gmail")
    logger.info("   Found 18 emails from Outlook")
    logger.info("   Found 12 emails from iCloud")

    logger.info("")
    logger.info("✅ Fetch complete! Total: 55 emails")

    print()
    print("=" * 60)
    print(f"✓ Logs saved to: logs/job_tracker.log")
    print("  (Check the file to see all DEBUG messages)")
    print("=" * 60)