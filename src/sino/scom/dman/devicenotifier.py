# -*- coding: utf-8 -*-
#

from .devicesubscriber import DeviceSubscriber


class DeviceNotifier(object):
    """Interface needed by the DeviceSubscriber class.

    Have a look on the DeviceManager class to see an implementation of this interface.
    """

    def subscribe(self, device_subscriber, filter_policy=('all',)):
        """Adds the given subscriber to the list.

        :param device_subscriber Subscriber to be added to the list
        :type device_subscriber DeviceSubscriber
        :param filter_policy The list of device types of interest
        :type filter_policy tuple[string]
        :return True if subscriber could be added, otherwise False
        """
        pass

    def unsubscribe(self, device_subscriber):
        """Removes the given subscriber from the list.

        :param device_subscriber Subscriber to be removed from the list
        :type device_subscriber DeviceSubscriber
        :return True if subscriber could be removed, otherwise False
        """
        pass
