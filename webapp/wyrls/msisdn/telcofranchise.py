import re
try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        import xml.etree.ElementTree as etree


class SimpleLookup(object):

    def __init__(self, xml_file=None):
        if xml_file:
            self.load_from_xml_file(xml_file)

    def load_from_xml_file(self, xml_file):
        f = xml_file
        if not isinstance(f, file):
            f = file(xml_file)
        self.tree = etree.parse(f)
        self.root = self.tree.getroot()
        self.all_patterns = [ ]
        for nr in self.root.getchildren():
            self.all_patterns.append( 
                {   'range': nr.find('range').text, 
                    'network': nr.find('network').text,
                    'type': nr.find('type').text,
                }
                )
    
    def resolve_network(self, msisdn):
        network = None
        for p in self.all_patterns:
            if re.match(p['range'], msisdn):
                network = p['network']
                break
        return network

    def resolve_type(self, msisdn):
        mtype = None
        for p in self.all_patterns:
            if re.match(p['range'], msisdn):
                mtype = p['type']
                break
        return mtype
            

if __name__ == "__main__":
    import os
    tf = SimpleLookup(xml_file=os.path.join(os.path.dirname(__file__),"../../../franchise.xml"))
    """
    for i in xrange(1,100000):
        net = tf.resolve_network("09202177276")
    print net
    """
