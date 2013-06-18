#!/usr/bin/env python
#-------------------------------------------------------------------------------
import weakref
from xml.etree.ElementTree import TreeBuilder, tostring, fromstring
#-------------------------------------------------------------------------------
__all__ = ["XMLBuilder"]

__doc__ = """
XMLBuilder is tiny library build on top of ElementTree.TreeBuilder to
make xml files creation more pythonomic. `XMLBuilder` use `with`
statement and attribute access to define xml document structure.

from __future__ import with_statement # only for python 2.5
from xmlbuilder import XMLBuilder

x = XMLBuilder('root')
x.some_tag
x.some_tag_with_data('text', a='12')

with x.some_tree(a='1'):
    with x.data:
        x.mmm
        for i in range(10):
            x.node(val=str(i))

etree_node = ~x # <= return xml.etree.ElementTree object
print str(x) # <= string object

will result:

<?xml version="1.0" encoding="utf-8" ?>
<root>
    <some_tag />
    <some_tag_with_data a="12">text</some_tag_with_data>
    <some_tree a="1">
        <data>
            <mmm />
            <node val="0" />
            <node val="1" />
            <node val="2" />
            <node val="3" />
            <node val="4" />
            <node val="5" />
            <node val="6" />
            <node val="7" />
            <node val="8" />
            <node val="9" />
        </data>
    </some_tree>
</root>

There some fields, which allow xml output customization:

formatted = produce formatted xml. default = True
tabstep   = tab string, used for formatting. default = ' ' * 4
encoding  = xml document encoding. default = 'utf-8'
xml_header = add xml header
                (<?xml version="1.0" encoding="$DOCUMENT_ENCODING$">)
            to begining of the document. default = True
builder = builder class, used for create dcument. Default =
                        xml.etree.ElementTree.TreeBuilder

Options can be readed by

x = XMLBuilder('root')
print x[option_name]

and changed by

x[option_name] = new_val

Happy xml'ing.
"""


class XMLNode(object):
    def __init__(self, doc, tag, *args, **kwargs):
        self.__document = doc
        self.__childs = []
        self.__tag = tag
        self.__attrs = {}
        self.__xml_update(args, kwargs)
    
    def __xml_update(self, args, kwargs):
        for arg in args:
            if not isinstance(arg, basestring):
                raise ValueError(
                    "Non-named arguments should be string only, not %r" \
                                    % (arg,))
                
        self.__childs.append("".join(args))
    
        for key, val in kwargs.items():
            if not isinstance(val, basestring):
                raise ValueError(
                    "Attribute values should be string only, not %r" \
                                    % (val,))
        self.__attrs.update(kwargs)
    
    def __setitem__(self, name, val):
        if not isinstance(val, basestring):
            raise ValueError("Attribute names should be string only, not %r" \
                                % (val,))

        if not isinstance(val, basestring):
            raise ValueError("Attribute values should be string only, not %r" \
                                % (val,))
        
        self.__attrs[name] = val
    
    def __getattr__(self, name):
        node = XMLNode(self.__document, name)
        self.__childs.append(node)
        return node
    
    def __call__(self, *args, **kwargs):
        self.__xml_update(args, kwargs)
        return self
    
    def __unicode__(self):
        return str(self).decode(self.__document()['encoding'])
        
    def __str__(self):
        return tostring(~self, self.__document()['encoding'])
    
    def __invert__(self):
        builder = self.__document()['builder']()
        self.__toxml(builder, 0)
        return builder.close()        
    
    def __child_tag_count(self):
        return len([child for child in self.__childs
                        if not isinstance(child, basestring)])
        
    def __toxml(self, builder, level):
        if self.__document()['formatted']:    
            tab = "\n" + self.__document()['tabstep'] * level
            builder.data(tab)
        else:
            tab = ""
            
        builder.start(self.__tag, self.__attrs)
        
        for child in self.__childs:
            if isinstance(child, basestring):
                builder.data(child)
            else:
                child.__toxml(builder, level + 1)
        
        if self.__child_tag_count() != 0 and tab:
            builder.data(tab)
            
        builder.end(self.__tag)
    
    def __lshift__(self, val):
        self.__xml_update([val], {})
        return self

    def __enter__(self):
        return self.__document()(self)
        
    def __exit__(self, x, y, z):
        self.__document()(None)


class XMLBuilder(object):
    def __init__(self, root_name, *args, **kwargs):
        root = XMLNode(weakref.ref(self), root_name, *args, **kwargs)
        self.__stack = [root]
        
        self.__opts = {
            'formatted' : True,
            'tabstep'  : ' ' * 4,
            'encoding'  : 'utf-8',
            'xml_header' : True,
            'builder' : TreeBuilder
        }
    
    def __getitem__(self, name):
        return self.__opts[name]

    def __setitem__(self, name, val):
        self.__opts[name] = val
    
    def __getattr__(self, name):
        return getattr(self.__stack[-1], name)
    
    def __lshift__(self, val):
        return self.__stack[-1] << val
    
    def __call__(self, obj):
        if obj is None:
            self.__stack.pop()
        else:
            self.__stack.append(obj)
            return self
    
    def __str__(self):
        if self['xml_header']:
            hdr = '<?xml version="1.0" encoding="%s" ?>\n' % self['encoding']
        else:
            hdr = ""
            
        return hdr + str(self.__stack[0])
    
    def __invert__(self):
        return ~self.__stack[0]

#-------------------------------------------------------------------------------
def make_text_attr(text, attrs_dict):
    if attrs_dict.items():
        attrs = ", ".join('{0}={1!r}'.format(name, val) 
                                for name, val in attrs_dict.items())
    else:
        attrs = ""

    if text and text.strip() != '':
        text = text.strip()
    else:
        text = ""
    
    if text and attrs:
        text_attr = "{0!r}, {1}".format(text, attrs)
    elif text:
        text_attr = repr(text)
    else:
        text_attr = attrs
    
    return text_attr

def xml2py(xml, name, tabstep=" " * 4):
    etree = fromstring(xml)
    text_attr = make_text_attr(etree.text, etree.attrib)

    if text_attr:
        res = "{0} = XMLBuilder({0!r}, {1})".format(name, text_attr)
    else:
        res = "{0} = XMLBuilder({1})".format(name)
    
    return res + "\n" + "\n".join(
        tabstep * tab + data for tab, data in _xml2py(etree, name))

def _xml2py(etree, name):

    childs = etree.getchildren()
    
    text_attr = make_text_attr(etree.text, etree.attrib)
    
    if len(childs) != 0:
        yield 0, "with {0}.{1}({2}):".format(name, etree.tag, text_attr)

        for elem in childs:
            for tab, data in _xml2py(elem, name):
                yield tab + 1, data
        
    else:
        yield 0, "{0}.{1}({2})".format(name, etree.tag, text_attr)
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        sys.stderr.write("Usage : {0} XML_FILE_NAME\n".format(sys.argv[0]))
    else:
        print(xml2py(open(sys.argv[1]).read(), 'root'))
#-------------------------------------------------------------------------------
    
    
    
    