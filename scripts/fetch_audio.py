#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from logger import get_logger

from source_extractor import (
        vox_forge,
        constants
)


logger = get_logger(__name__)


def get_audio_url_collection(url):
    if url == vox_forge.CATALOG_URL:
        vox_forge.runner()
    else:
        logger.error('No valid source URL specified')
        return None


if __name__ == "__main__":
    if not os.path.exists(constants.OUTPUT_DIR):
        try:
            logger.info("Making new directory %s", constants.OUTPUT_DIR.format(''))
            os.makedirs(constants.OUTPUT_DIR.format(''))
        except OSError as e:
            logger.info("Files exist, not writing new directory: %s", constants.OUTPUT_DIR.format(''))
        try:
            logger.info("Making new directory %s", constants.CATEGORIZED_DIR)
            os.makedirs(constants.CATEGORIZED_DIR)
        except OSError as e:
            logger.info("Files exist, not writing new directory: %s", constants.CATEGORIZED_DIR)
    print 'Done'
