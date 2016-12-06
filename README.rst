py3status-cmus
==============

This is a module for py3status_ to control and show information related to cmus_ music player.

py3status-cmus allows sending basic control commands to local or remote cmus by mouse button presses on i3 status bar.

.. _py3status: https://github.com/ultrabug/py3status

.. _cmus: https://cmus.github.io/

**Examples**

.. image:: doc/img/playing_progress_bar.png
*Playing*

.. image:: doc/img/paused_progress_bar.png
*Paused*

.. image:: doc/img/stopped_progress_bar.png
*Stopped*

.. image:: doc/img/paused_no_progress_bar.png
*Paused (no progress bar)*

Requirements
------------

It is assumed that you have working i3bar with py3status already installed.
If not, look at py3status install_ for more information.

.. _install: https://github.com/ultrabug/py3status#installation

Make sure that *cmus-remote* can be found in your PATH.

.. code::

	$ which cmus-remote
	/usr/bin/cmus-remote

Installing
----------

Clone the repository to preferred location:

.. code::

	$ git clone https://github.com/oljo/py3status-cmus.git

py3status modules are normally installed in ~/.i3/py3status/ directory.

If this directory doesn't exist you should create it:

.. code::

        $ mkdir ~/.i3/py3status/

Copy cmus_status.py to py3status directory:

.. code::

	$ cp py3status-cmus/cmus_status.py ~/.i3/py3status/

Enable the module in your py3status config:

.. code::

	order += "cmus_status"

Configuration
-------------
Configuration should be done in py3status config file:

.. code::

	 cmus_status {
		output_format = "%status% %artist% - %album% - %title%"
		show_progress_bar = false
	        show_playtime = true
		progress_bar_length = 10
		on_click 1 = "exec cmus-remote -u"
	}

Parameters:

* cache_timeout  
* output_format
* show_progress_bar 
* progress_bar_length
* not_running_msg 
* nothing_playing_msg 
* cmus_args
* show_playtime 

**output** defines the basic format for the output status.

Variables defined between %-characters should match to **cmus-remote -Q** output with *set* and *tag* omitted.

e.g. in following example %genre% would match to "Folk Rock".

.. code::

	$ cmus-remote -Q
	status playing
	file /home/user/music/Bob Dylan - Nashville Skyline/Bob Dylan - Girl From The North Country.flac
	duration 224
	position 15
	tag album Nashville Skyline
	tag artist Bob Dylan
	tag date 1969
	tag genre Folk Rock
	tag title Girl From The North Country
	tag tracknumber 01
	set aaa_mode all
	set continue true
	set play_library true
	set play_sorted false
	set replaygain disabled
	set replaygain_limit true
	set replaygain_preamp 0.000000
	set repeat false
	set repeat_current false
	set shuffle false
	set softvol false
	set vol_left -1
	set vol_right -1

**not_running_msg** and **nothing_playing_msg** are status outputs when cmus is not running or if nothing is playing in cmus.

These can be set to "" to get empty status string.

To disable progress bar set **show_progress_bar** to false.
**progress_bar_length** defines length of the progress bar in characters.

**cmus_args** defines arguments that are forwarded to cmus-remote.
If you use different socket than default ~/.cmus/socket or you want the status from remote cmus, you can specify it here by using "--server" argument.

e.g.

.. code:: 

	cmus_args = "--server 192.168.1.10" 

**cache_until** defines how often status is updated (in seconds).

On click
--------

Mouse buttons 1-5 can be set in py3status configuration file using on_click:

.. code:: 

	cmus_status {
	        output_format = "%status% %artist% - %album% - %title%"
	        show_progress_bar = false
	        show_playtime = true
		on_click 1 = "exec cmus-remote -u"
	}

If your mouse has buttons with larger numbers (e.g. 8 and 9 for page backward and forward) they can be mapped to click events in cmus_status.py:

.. code:: python

	ON_CLICK_MAP = {
        	        9 : [CMUS_CMD] + ["-n"], # Next track
                	8 : [CMUS_CMD] + ["-r"]  # Previous track
               		}

xev_ can be used to find out mouse button numbers.

.. _xev: https://www.x.org/archive/X11R7.7/doc/man/man1/xev.1.xhtml
