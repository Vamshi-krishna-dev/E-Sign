import logging

logger = logging.getLogger("E-Sign")
logger.setLevel(logging.INFO)

# Console handler (no folder, no files)
handler = logging.StreamHandler()

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)

