import unittest
import urlencodeddict

VALUES = [
    {'encoded': u"name=Eric+Moritz&children=Aiden+Moritz&children=Ethan+Moritz",
     'decoded': {'name': u"Eric Moritz",
                 'children': ['Aiden Moritz', 'Ethan Moritz']}
     },
    {'encoded': u"name=Eric+Moritz&parents.0.name=William+Moritz&parents.1.name=Joyce+Moritz",
     'decoded': {'name': u"Eric Moritz",
                 'parents': [{'name': u"William Moritz"}, {'name': u"Joyce Moritz"}]},
     },
]

class TestLoads(unittest.TestCase):
    
    def test_loads(self):
        for v in VALUES:
            input, expect = v['encoded'], v['decoded']

            result = urlencodeddict.loads(input)
            self.assertEqual(expect, result)


class TestDumps(unittest.TestCase):
    
    def test_dumps(self):
        for v in VALUES:
            input, expect = v['decoded'], v['encoded']
            
            result = urlencodeddict.dumps(input)

            self.assertEqual(expect, result)
