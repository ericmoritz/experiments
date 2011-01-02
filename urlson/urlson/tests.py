import unittest
import urlson


VALUES = [
    {'encoded': u"name=Eric+Moritz&children=Aiden+Moritz&children=Ethan+Moritz",
     'decoded': {'name': u"Eric Moritz",
                 'children': ['Aiden Moritz', 'Ethan Moritz']}
     },

    # There's no way to produce a empty list when decoding
    {'encoded': u"name=Eric+Moritz",
     'decoded': {'name': u"Eric Moritz"},},

    {'dumps': {'name': u"James Buchanan", "children": []},
     'result': u"name=James+Buchanan"},
]


class TestLoads(unittest.TestCase):
    
    def test_loads(self):
        for v in VALUES:
            if "encoded" in v:
                input, expect = v['encoded'], v['decoded']

                result = urlson.loads(input)
                self.assertEqual(expect, result)


class TestDumps(unittest.TestCase):
    
    def test_dumps(self):
        for v in VALUES:
            input = expect = None

            if "dumps" in v:
                input = v['dumps']
                expect = v['result']
            elif "encoded" in v:
                input, expect = v['decoded'], v['encoded']

            if input:
                result = urlson.dumps(input)
                self.assertEqual(expect, result)
