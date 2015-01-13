#!/usr/bin/env python


import unititest

def fun(x):
        return x+1

class MyTest(unititest.TestCase):
        def test(self):
                self.assertEqual(fun(3), 5)


if __name__ == "__main__":
    p = MyTest()
    p.test()


