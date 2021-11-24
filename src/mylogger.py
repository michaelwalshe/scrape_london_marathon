import logging
import logging.handlers
import sys

import autologging


def setup_pipeline_level_logger(
    file_name: str = None,
    trace: bool = False
) -> logging.Logger:
    """Create instance of overall logger"""

    # Format and extended format to use in logger output
    basic_format = "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s"
    trace_format = (
        "%(asctime)s:%(process)s:%(levelname)s:%(filename)s"
        ":%(lineno)s:%(name)s:%(funcName)s:%(message)s"
    )

    # Setup basic logger and console output, note that level here is the minimum
    # that will be output
    logging.basicConfig(
        format=basic_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        level=autologging.TRACE,
    )

    # Create the logging object
    logger = logging.getLogger()

    # Create an email handler for warnings, this will only output when
    # a warning occurs
    email_hdlr = logging.handlers.SMTPHandler(
        mailhost='amadeus-co-uk.mail.protection.outlook.com',
        fromaddr='process@amadeus.co.uk',
        toaddrs=['michael.walshe@amadeus.co.uk'],
        subject='Sample Log Mail',
        secure=None
    )
    formatter = logging.Formatter(trace_format)
    email_hdlr.setFormatter(formatter)
    email_hdlr.setLevel(logging.WARNING)
    logger.addHandler(email_hdlr)

    # If passed a filename, setup file logs
    if file_name is not None:
        log_hdlr = logging.FileHandler(f"{file_name}.log")
        formatter = logging.Formatter(basic_format)
        log_hdlr.setFormatter(formatter)
        log_hdlr.setLevel(logging.DEBUG)
        logger.addHandler(log_hdlr)

        # If setting up a TRACE log then add that handler
        if trace:
            trace_hdlr = logging.FileHandler(f"{file_name}_trace.log")
            formatter = logging.Formatter(trace_format)
            trace_hdlr.setFormatter(formatter)
            trace_hdlr.setLevel(autologging.TRACE)
            logger.addHandler(trace_hdlr)
    return logger


def handle_exception(exc_type, exc_value, exc_traceback):
    """Sends uncaught exceptions to the log"""

    # Allow ending program using Ctrl + C
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger()

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def catch_errors():
    """Enable handle_exception to catch all exceptions and log"""
    sys.excepthook = handle_exception
    return None
