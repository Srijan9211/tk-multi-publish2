# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

logger = sgtk.platform.get_logger(__name__)


class Task(object):
    """
    A task is a particular unit of work which can to be carried
    by the publishing process. A task can be thought of as a
    'plugin instance', e.g a particular publishing plugin operating
    on a particular collector item.
    """

    def __init__(self, plugin, item, settings):
        """
        :param plugin: The plugin instance associated with this task
        :param item: The collector item associated with this task
        :param bool visible: Indicates that the task is visible
        :param bool enabled: Indicates that the task is enabled
        :param bool checked: Indicates that the task is checked
        :param dict settings: Initial settings to use for task
        """
        self._plugin = plugin
        self._item = item
        self._settings = settings
        self._accepted = False
        self._visible = True
        self._enabled = True
        self._checked = True

    def __repr__(self):
        """
        String representation
        """
        return "<Task: %s for %s >" % (self._plugin, self._item)

    @classmethod
    def create_task(cls, plugin, item, settings):
        """
        Factory method for new tasks.

        :param plugin: Plugin instance
        :param item: Item object
        :param is_visible: bool to indicate if this option should be shown
        :param is_enabled: bool to indicate if node is enabled (clickable)
        :param is_checked: bool to indicate if this node is checked
        :param settings: dict of initial settings to use for task
        :return: Task instance
        """
        task = Task(plugin, item, settings)
        plugin.add_task(task)
        item.add_task(task)
        logger.debug("Created %s" % task)
        return task

    def is_same_task_type(self, other_task):
        """
        Indicates if this plugin instance wraps the same plugin type as another
        plugin instance.

        :param other_task: The other plugin to test against.
        :type other_task: :class:`Task`
        """
        return self._plugin == other_task._plugin

    @property
    def item(self):
        """
        The item associated with this Task
        """
        return self._item

    @property
    def plugin(self):
        """
        The plugin associated with this Task
        """
        return self._plugin

    @property
    def visible(self):
        """
        Returns if this Task should be visible in the UI.
        Invisible tasks are still processed but not seen in the UI
        """
        return self._visible

    @property
    def checked(self):
        """
        Returns if this task should be turned on or off by default
        """
        return self._checked

    @property
    def enabled(self):
        """
        Returns if this task's checked state can be manipulated by the user or not.
        """
        return self._enabled

    @property
    def settings(self):
        """
        Dictionary of settings associated with this Task
        """
        return self._settings

    @settings.setter
    def settings(self, settings):
        # setter for value
        self._settings = settings

    def accept(self):
        """
        Accept this task
        """
        accept_data = self.plugin.run_accept(self.settings, self.item)
        if accept_data.get("accepted"):

            # this item was accepted by the plugin!

            # log the acceptance and display any extra info from the plugin
            self.plugin.logger.info(
                "Plugin: '%s' - Accepted: %s" % (self.plugin.name, self.item.name),
                extra=accept_data.get("extra_info")
            )

            # look for bools accepted/visible/enabled/checked

            # TODO: Implement support for this!
            # all things are visible by default unless stated otherwise
            self._visible = accept_data.get("visible", True)

            # all things are enabled by default unless stated otherwise
            self._enabled = accept_data.get("enabled", True)

            # only update node selection if this wasn't previously accepted
            if not self._accepted:
                self._accepted = True

                # all things are checked by default unless stated otherwise
                self._checked = accept_data.get("checked", True)

        # Else disable and uncheck this task
        else:
            self.plugin.logger.info(
                "Plugin: '%s' - Rejected: %s" % (self.plugin.name, self.item.name),
                extra=accept_data.get("extra_info")
            )
            self._accepted = False
            self._enabled = False
            self._checked = False

    def validate(self):
        """
        Validate this Task

        :returns: True if validation succeeded, False otherwise.
        """
        return self.plugin.run_validate(self.settings, self.item)

    def publish(self):
        """
        Publish this Task
        """
        self.plugin.run_publish(self.settings, self.item)

    def finalize(self):
        """
        Finalize this Task
        """
        self.plugin.run_finalize(self.settings, self.item)
