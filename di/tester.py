import importlib
import argparse

def exec_tests():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str)
    args = parser.parse_args()
    try:
        mode = args.mode
    except AttributeError as e:
        mode = None
    if mode == "run":
        mode = None
    passed = 0
    total = 0
    i = 0
    while True:
        i += 1
        try:
            t = importlib.import_module("t" + str(i))
            total += 1
            if True == t.test(mode):
                passed += 1
        except ModuleNotFoundError:
            break
    if mode != 'record':
        print(f'{passed}/{total} passed')

if __name__ == '__main__':
    exec_tests()