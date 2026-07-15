import contextvars
import json
import logging
import sys

# ContextVar to store the per-request correlation ID
correlation_id_var = contextvars.ContextVar("correlation_id", default=None)

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Fetch the correlation ID from context
        correlation_id = correlation_id_var.get()
        
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if correlation_id:
            log_data["correlation_id"] = correlation_id
            
        # Extract custom fields from extra
        standard_attrs = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
            'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'message', 'asctime'
        }
        
        extra_fields = {}
        for key, val in record.__dict__.items():
            if key not in standard_attrs:
                extra_fields[key] = val
                
        # Extract "event" if specified in extra, otherwise default it
        event = extra_fields.pop("event", None)
        if event:
            log_data["event"] = event
        else:
            log_data["event"] = "generic_log"
            
        if extra_fields:
            log_data["fields"] = extra_fields
            
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logging(level: int = logging.DEBUG):
    """
    Set up the root logger to output structured JSON to stdout.
    """
    root_logger = logging.getLogger()
    
    # Remove existing handlers to prevent duplicate logging
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
        
    # Configure StreamHandler for stdout only
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(JsonFormatter())
    
    root_logger.addHandler(stream_handler)
    root_logger.setLevel(level)

    # Prevent logs from double-propagating to default handlers
    root_logger.propagate = False
