#!/usr/bin/env python
"""
BTRFS-Snap.py

:License: The MIT License (MIT)
:Company: SwissTech Consulting
:Author: Patrick Glass <patrickglass@swisstech.ca>
:Copyright: Copyright 2015 SwissTech Consulting

Allows the user to setup automatic snapshots of btrfs subvolumes using
crontab. With a central config file each subvolume can have independant
snapshot intervals and retension without verbose crontabs.
"""
import os
import sys
import yaml
import syslog
import datetime
import argparser
import subprocess


CONFIG_FILE = '/etc/btrfs-snappy.conf'
DEFAULT_CONFIG = """
#
# btrfs-snap.py
#
# Configuration file for btrfs-snap.py which allows specifying the subvolumes
# to snapshot as well as the customization of the retention as well

# These are the targets passed in from cron schedule
# the value specified the number of snapshots of each category to retain.
retention:
    default:
        minute:   0
        hourly:  24
        daily:    7
        weekly:   4
        monthly:  4
        yearly:   0
    short_term: &short
        minute:   4
        hourly:   4
        daily:    0
        weekly:   0
        monthly:  0
        yearly:   0
    long_term: &long
        minute:   0
        hourly:   4
        daily:    7
        weekly:   4
        monthly: 12
        yearly:   5

# Here you specify the subvolumes which are to be snapshotted. The name does
# not matter and is just used to keep things organized.
locations:
    root:
        subvolume: /
        retention: *short
    var: /var
    # tmp: /tmp
    home:
        subvolume: /home
        retention: *long
"""


class Snappy(object):

    def __init__(self, config_file, default_config):
        self.config = {}
        self.config_file = config_file
        self.default_config = default_config

        if self.load_validate_config(config_file)
            syslog.syslog("Loaded config from %s" % config_file)
        else:
            # FIXME: This is just temporary for quick testing
            self.config = yaml.load(default_config)
            syslog.syslog(syslog.LOG_ERR, "DEBUG: FIXME: Loading defaults!!")


    def load_validate_config(config_file):
        """This function will check the config variable and ensure that
        the most basic sections are present
        """
        if os.path.exists(config_file):
            self.config = yaml.load(file(config_file))
            syslog.syslog("Loaded config from %s" % config_file)
        else:
            msg = "Could not find %s. Loading Defaults." % config_file
            syslog.syslog(syslog.LOG_ERR, msg)
        if not config:
            msg = "YAML config file was empty."
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        if 'retention' not in config:
            msg = "retention section in config file could not be found."
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        if 'default' not in config['retention']:
            msg = "retention section in config file could not be found."
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        for named_retention in config['retention']:
            schedules = [
                'minute',
                'hourly',
                'daily',
                'weekly',
                'monthly',
                'yearly'
            ]
            for t in schedules:
                if not hasattr(named_retention, 'minute'):
                    msg = "%s is missing retention integer for %s" % (named_retention, t)
                    syslog.syslog(syslog.LOG_ERR, msg)
                    return False
        if 'locations' not in config:
            msg = "locations section in config file could not be found."
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        if len(config['retention']) < 1:
            msg = "you must have at least one subvolume location defined."
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        return True

    def write_config(self):
        with open("filename.txt", 'w') as f:
            f.write(default_config)

    def log_error(self, message):
        syslog.syslog(syslog.LOG_ERR, message)

    def create(self, name):
        subvol = self.config['locations'][name]

    def purge_old(self, name):
        pass


def main():
    s = Snappy(CONFIG_FILE, DEFAULT_CONFIG)

    s.create('hourly')
    s.purge_old('hourly')


if __name__ == "__main__":
    ret_code = main()
    sys.exit(ret_code)
