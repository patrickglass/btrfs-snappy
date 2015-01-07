btrfs-snappy
============

BTRFS Automatic Snapshot Utility allows the user to setup automatic snapshots
of btrfs subvolumes using crontab. With a central config file each subvolume
can have independant snapshot intervals and retension without verbose crontabs.

Quick-Start
-----------

Download the main executable and put it somewhere on the path

    cd /usr/local/bin/
    sudo wget https://raw.githubusercontent.com/patrickglass/btrfs-snappy/master/btrfs-snap.py
    sudo chmod 700 btrfs-snap.py
    sudo btrfs-snap.py --create_config


Edit this config file and ensure you have specified all of your subvolumes

    vi /etc/btrfs-snappy.conf


The locations are specified with a name, the subvolume path, and the optional
rentention if you do not want the default.

    locations:
        <friendly_name>:
            subvolume: <path_to_my_subvolume>
            retention: *default


Example using default retension and btrfs root system

    locations:
        root:
            subvolume: /
            retention: *short
        var: /var
        home:
            subvolume: /home
            retention: *long


Example of secondary mount with media and personal subvolumes

    locations:
        main:
            subvolume: /nas
            retention: *short
        movies:
            subvolume: /nas/media/movies
            retention: *short
        tv_shows:
            subvolume: /nas/media/tv_shows
            retention: *short
        downloads:
            subvolume: /nas/media/downloads
            retention: *short
        work:
            subvolume: /nas/work
            retention: *long
        personal: /nas/personal_vol


Now one must setup crontab to call this new executable at regular intervals.

    sudo crontab -e

Use the following as an example

    # m   h  dom mon dow  command
    */15  *   *   *   *   btrfs-snap.py minute
    0     *   *   *   *   btrfs-snap.py hourly
    0     0   *   *   *   btrfs-snap.py daily
    0     0   *   *   0   btrfs-snap.py weekly
    0     0   1   *   *   btrfs-snap.py monthly
    0     0   1   1   *   btrfs-snap.py yearly

