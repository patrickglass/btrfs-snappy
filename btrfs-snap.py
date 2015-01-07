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
import argparse
import subprocess


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

    def __init__(self, config_file, default_config, verbose=True):
        self.config = {}
        self.config_file = config_file
        self.default_config = default_config
        self.verbose = verbose

        if self.load_validate_config(config_file):
            syslog.syslog("Loaded config from %s" % config_file)
        else:
            # FIXME: This is just temporary for quick testing
            self.config = yaml.load(default_config)
            syslog.syslog(syslog.LOG_ERR, "DEBUG: FIXME: Loading defaults!!")


    def load_validate_config(self, config_file):
        """This function will check the config variable and ensure that
        the most basic sections are present
        """
        if os.path.exists(config_file):
            self.config = yaml.load(file(config_file))
            syslog.syslog("Loaded config from %s" % config_file)
        else:
            msg = "Could not find %s. Loading Defaults." % config_file
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        if not self.config:
            msg = "YAML config file was empty."
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        if 'retention' not in self.config:
            msg = "retention section in config file could not be found."
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        if 'default' not in self.config['retention']:
            msg = "retention section in config file could not be found."
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        for named_retention in self.config['retention']:
            schedules = [
                'minute',
                'hourly',
                'daily',
                'weekly',
                'monthly',
                'yearly'
            ]
            for t in schedules:
                if not hasattr(named_retention, t):
                    msg = "%s is missing retention integer for %s" % (named_retention, t)
                    syslog.syslog(syslog.LOG_ERR, msg)
                    return False
        if 'locations' not in self.config:
            msg = "locations section in config file could not be found."
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        if len(self.config['locations']) < 1:
            msg = "you must have at least one subvolume location defined."
            syslog.syslog(syslog.LOG_ERR, msg)
            return False
        for location in self.config['locations']:
            loc_attr = [
                'subvolume',
                'retention'
            ]
            for t in loc_attr:
                if not hasattr(location, t):
                    msg = "%s is missing attribute %s" % (location, t)
                    syslog.syslog(syslog.LOG_ERR, msg)
                    return False
        if self.verbose:
            print "Loaded Configuration: %s" % self.config
        return True

    def write_config(self):
        # Check the directory to ensure the users has correct permissions
        path = os.path.dirname(self.config_file)
        if not os.access(path, os.W_OK):
            msg = "You do not have write permissions to directory %s" % path
            syslog.syslog(syslog.LOG_ERR, msg)
            raise RuntimeError("You do not have write permissions to directory %s" % path)
        with open(self.config_file, 'w') as f:
            f.write(self.default_config)

    def log_error(self, message):
        syslog.syslog(syslog.LOG_ERR, message)

    def create(self, interval):
        locations = self.config['locations']
        for name in locations:
            location = locations[name]
            # This is for the case with the manually specified subvol and retention.
            if 'subvolume' in location and 'retention' in location:
                subvol = location['subvolume']
                retention = location['retention']
            else:
                # Condensed format for specifying subvolume with default retention
                subvol = location
                retention = self.config['retention']['default']

            if interval not in retention:
                msg = "%s is missing attribute %s" % (retention, interval)
                syslog.syslog(syslog.LOG_ERR, msg)

            retention = retention[interval]
            print "%s:\n\tsubvolume: %s\n\tretention: %s\n" % (name, subvol, retention)
        # subvol = self.config['locations'][name]

    def purge_old(self, name):
        pass


def main():
    parser = argparse.ArgumentParser(description='Creates snapshots of btrfs subvolumes.')
    
    parser.add_argument('interval', nargs='?', choices=[
                        'minute', 'hourly', 'daily', 'weekly', 'monthly', 'yearly'],
                        help='''specify the interval prefix used to name all snapshots
                            and for tracking the number of snapshots to keep.''')
    parser.add_argument('--create_config', action='store_true',
                       help='Creates a new default config file at the location `--config`')
    parser.add_argument('-c', '--config',
                        default='/etc/btrfs-snappy.conf',
                        help='''specify the location of the yaml config file 
                            (default: /etc/btrfs-snappy.conf)''')
    parser.add_argument('-d', '--destination',
                        default='./snapshots/',
                        help='''specify the location to place the snapshots 
                            (defaults to .snapshots directory at the root of 
                            the subvolume)''')
    parser.add_argument("-q", "--quiet",
                        action="store_false", dest="verbose",
                        default=True,
                        help="don't print status messages to stdout")

    args = parser.parse_args()

    s = Snappy(args.config, DEFAULT_CONFIG, args.verbose)

    # Create config file based on default
    if args.create_config:
        s.write_config()
        msg = "default config has been written to %s" % (args.config)
        syslog.syslog(msg)
        return 0

    if not args.interval:
        parser.print_help()
        return 1
    
    s.create(args.interval)
    s.purge_old(args.interval)
    return 0


if __name__ == "__main__":
    ret_code = main()
    sys.exit(ret_code)
