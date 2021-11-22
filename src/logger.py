import logging
import sys

import autologging


def setup_pipeline_level_logger(
    file_name: str = None
) -> logging.Logger:
    """Create instance of overall logger"""

    logging.basicConfig(
        format='%(asctime)s: %(levelname)s: %(name)s: %(funcName)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        level=TRACE
    )

    logger = logging.getLogger()

    if file_name is not None:
        file_hdlr = logging.FileHandler(
            file_name
        )
        formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: %(funcName)s: %(message)s')
        file_hdlr.setFormatter(formatter)
        logger.addHandler(file_hdlr)

    return logger
