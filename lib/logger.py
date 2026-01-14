from datetime import datetime
import logging
import os
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_logger(log_file: str) -> logging.Logger:
    """
    Set up a logger with file handler.
    
    Args:
        log_file: Path to the log file
        
    Returns:
        Configured logger
    """
    # Create output directory if it doesn't exist
    output_dir = Path(log_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a new logger
    the_logger = logging.getLogger('toggl_to_jira')
    the_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers to avoid duplicates
    the_logger.handlers.clear()
    
    # Create file handler which logs INFO messages
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Create console handler with a higher level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    the_logger.addHandler(file_handler)
    the_logger.addHandler(console_handler)
    
    return the_logger

def check_existing_log(log_dir: str, file_name: str) -> bool:
    """
    Check if a log file exists with the given name pattern.
    
    Args:
        log_dir: Directory to check for logs
        file_name: Name of the file being processed
        
    Returns:
        True if a log file exists for the given file, False otherwise
    """
    log_path = Path(log_dir)
    # Get the file name without extension for pattern matching
    file_base = Path(file_name).stem
    
    # Check if any log file contains the base file name
    existing_logs = list(log_path.glob(f'*{file_base}*.log'))
    
    if existing_logs:
        logger.warning('Log files exist for %s', file_name)
        return True
        
    return False

def write_log_entries(logger: logging.Logger, records: List[Dict[str, Any]], log_type: str = 'success') -> None:
    """
    Write log entries.
    
    Args:
        logger: Logger to use for writing
        records: List of records to log
        log_type: Type of log entries (success or error)
    """
    log_function = logger.info if log_type == 'success' else logger.error
    
    for record in records:
        issue_id = record.get('issue_id', 'N/A')
        summary = record.get('summary', '')
        comment = record.get('comment', '')
        time_spent = record.get('time_spent', '')
        started = record.get('started', '')
        error = record.get('error', '')
        
        if log_type == 'success':
            log_function(
                'SUCCESS | issue=%s | summary="%s" | comment="%s" | timeSpent=%s | started=%s', 
                issue_id, summary,comment, time_spent, started
            )
        else:
            log_function(
                'ERROR | issue=%s | summary="%s" | comment="%s" | timeSpent=%s | started=%s | error=%s', 
                issue_id, summary, comment, time_spent, started, error
            )

def get_log_file_paths(file_path: str, output_dir: str = 'data/out') -> Dict[str, str]:
    """
    Get success and error log file paths for a given CSV file.
    
    Args:
        file_path: Path to the CSV file being processed
        output_dir: Directory for output files
        
    Returns:
        Dictionary with paths for success and error logs
    """
    file_name = Path(file_path).stem
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_filename = f"{file_name}_{timestamp}"
    
    return {
        'success': str(output_path / f"{base_filename}_success.log"),
        'error': str(output_path / f"{base_filename}_error.log")
    }
