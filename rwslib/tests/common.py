# -*- coding: utf-8 -*-

__author__ = 'glow'

from xml.etree import cElementTree as ET


def obj_to_doc(obj, *args, **kwargs):
    """Convert an object to am XML document object
    :rtype: xml.etree.ElementTree.Element
    """
    builder = ET.TreeBuilder()
    obj.build(builder, *args, **kwargs)
    return builder.close()


