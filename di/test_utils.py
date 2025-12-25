
from inspect import signature
from typing import Literal, Callable
from contextlib import ExitStack
import os
import sys

def compare_files(f1, f2):
    with ExitStack() as st:
        c1 = st.enter_context(open(f1, "r")).read()
        c2 = st.enter_context(open(f2, "r")).read()
        return c1 == c2
def run_test(mode: Literal["record", "record[all]", None], test_id: str, test_func: Callable[..., any], *args, **kwargs):
    expected_folder = "./test_expected_output"
    actual_folder = "./test_output"

    test_func_sig = signature(test_func)
    test_func_sig.bind(*args, **kwargs)
    assert mode == None or mode in ["record", "record[all]"], "Please provide correct CLI arguments!!!"
    if mode == None:
        expected_file_path = f"{expected_folder}/{test_id}.txt"
        assert os.path.isfile(expected_file_path), "record correct result first(manually or automatically)!"
        if not os.path.isdir('./test_output'):
            os.mkdir('./test_output')
        old_fd = sys.stdout
        actual_file_path = f"{actual_folder}/{test_id}.txt"
        with open(actual_file_path, "x") as sys.stdout:
            test_func(*args, **kwargs)
        sys.stdout = old_fd
        return compare_files(expected_file_path, actual_file_path)
    else:
        if not os.path.isdir('./test_expected_output'):
            os.mkdir("./test_expected_output")
        if mode == 'record[all]' or not os.path.isfile(f"./test_expected_output/{test_id}.txt"):
            old_fd = sys.stdout
            with open(f"./test_expected_output/{test_id}.txt", "x") as sys.stdout:
                test_func(*args, **kwargs)
            sys.stdout = old_fd