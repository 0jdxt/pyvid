from typing import Tuple

import os
import random
import re
import string

from hypothesis import given
from hypothesis.strategies import text
from hurry.filesize import size

from pyvid.classes import Logger


def generate_stats(n: int) -> Tuple[str, str, str]:
    chars = string.digits + string.ascii_letters + string.punctuation
    original = 0
    converted = 0
    strs = ""

    for _ in range(n):
        name_len = random.randint(10, 30)
        name = "".join(random.choices(chars, k=name_len))

        fsize = random.randint(10 ** 3, 10 ** 6)
        original += fsize

        comp = round(fsize * 20 / 100)
        converted += comp

        strs += f"{name}:{fsize}:{comp}\n"

    return strs[:-1], size(original), size(converted)


@given(text(alphabet=string.ascii_letters + string.digits + string.punctuation))
def test_logger(s: str) -> None:
    fname = "test_stats.txt"
    logger = Logger(fname)
    test_str = "TESTSTR" * 10
    logger.log(s)

    assert logger.get(1) == [s + "\n"]


def test_summ() -> None:
    fname = "test_stats.txt"
    logger = Logger(fname)
    logger.reset()

    n_lines = 500
    out, orig, conv = generate_stats(n_lines)
    logger.log(out)
    ex_out = re.findall("(.*$\n)", out + "\n", re.M)[-n_lines:]

    assert logger.get(n_lines) == ex_out

    logger.summarise(n_lines)
    ll = logger.get(1)[0]
    rex = r"(?P<p>\d+)%.+ (?P<o>\d{1,3}[BKMG]) -> (?P<c>\d{1,3}[BKMG])$"
    summary_re = re.compile(rex)
    m = summary_re.search(ll)

    assert m
    assert m.group("o") == orig
    assert m.group("c") == conv
    assert "19" <= m.group("p") <= "20"

    os.remove(fname)
