import json
import os
import logging

from boxmaker import base_dir

logger = logging.getLogger(__name__)


# load ads from config file
ad_config_file_path = os.path.join(base_dir, 'config', 'ads.json')
ad_config = []
with open(ad_config_file_path, 'r') as f:
    ad_config = json.load(f)
logging.info("Loaded {} ads".format(len(ad_config)))

# clean up text
for ad in ad_config:
    ad['text'] = ad['text'].replace('URL', ad['url'])


def visible_ads():
    # TODO: respect start and end dates
    return ad_config
