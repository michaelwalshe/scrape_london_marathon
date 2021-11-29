"""
/******************************************************************************
*                                                                             *
*  Name:             mylogger.py                                              *
*                                                                             *
*  Description:      A module to setup a custom logger with default options   *
*                    Can setup multiple logs with different levels of info    *
*                    in each, and an email log for errors, as well as handling*
*                    all uncaught exceptions.      				              *
*                                                                             *
*  Creation Date:    19 05 2021                                               *
*                                                                             *
*  Created By:       Michael Walshe                                           *
*                    Amadeus Software Ltd                                     *
*                    michael.walshe@amadeus.co.uk                             *
*                    +44 (0) 1993 848010                                      *
*                                                                             *
*  Edit History:                                                              *
*  +------------------+------------+---------------------------------------+  *
*  |    Programmer    | Date       | Description                           |  *
*  +------------------+------------+---------------------------------------+  *
*  | Michael Walshe   | 25NOV2021  | Original.                             |  *
*  +------------------+------------+---------------------------------------+  *
******************************************************************************/
"""
import logging
import logging.handlers
import sys

# Get things for type hinting
from typing import Optional, Type
from types import TracebackType

import autologging


def setup_logger(
    file_name: Optional[str] = None,
    trace_log: bool = False,
    catch_errors: bool = True,
    **kwargs,
) -> logging.Logger:
    """Create instance of overall logger

    Args:
        file_name: Optional, the name/path to the output logs, without a file extension
        trace_log: Optional, twhether to output a detailed TRACE log
        catch_errors: Replace python standard sys.excepthook with a new exception
            handler that sends them to the log.
        **kwargs: Arguments for logging.handlers.SMTPHandler, see logging documentation
            for details
    """

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
    if kwargs:
        email_hdlr = logging.handlers.SMTPHandler(**kwargs)
        formatter = logging.Formatter(trace_format)
        email_hdlr.setFormatter(formatter)
        email_hdlr.setLevel(logging.WARNING)
        logger.addHandler(email_hdlr)

    # If passed a filename, setup file logs
    if file_name:
        log_hdlr = logging.FileHandler(f"{file_name}.log")
        formatter = logging.Formatter(basic_format)
        log_hdlr.setFormatter(formatter)
        log_hdlr.setLevel(logging.DEBUG)
        logger.addHandler(log_hdlr)

        # If setting up a TRACE log then add that handler
        if trace_log:
            trace_hdlr = logging.FileHandler(f"{file_name}_trace.log")
            formatter = logging.Formatter(trace_format)
            trace_hdlr.setFormatter(formatter)
            trace_hdlr.setLevel(autologging.TRACE)
            logger.addHandler(trace_hdlr)

    if catch_errors:
        # Replaces excepthook with our own exception handler
        sys.excepthook = handle_exception
    return logger


def handle_exception(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType,
) -> None:
    """Sends uncaught exceptions to the log"""

    # Allow ending program using Ctrl + C
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger()

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
