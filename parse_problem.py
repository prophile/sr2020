from __future__ import annotations

import re
import sys
import sexpdata
from typing import IO, Any, NamedTuple, Dict


def strip_symbols(sexp: Any) -> Any:
    if isinstance(sexp, sexpdata.Symbol):
        return sexp.value()
    elif isinstance(sexp, list):
        return [strip_symbols(x) for x in sexp]
    else:
        return sexp


DEFNAME = re.compile(r'r(\d+)m(\d+)z(\d+)')


class Definition(NamedTuple):
    round: int
    match: int
    zone: int

    @classmethod
    def from_name(cls, name: str) -> Definition:
        match = DEFNAME.match(name)
        if match is None:
            raise ValueError(f"Cannot parse name {name!r}")
        return cls(int(match.group(1)), int(match.group(2)), int(match.group(3)))


def parse_solution(src: IO[str]) -> Dict[Definition, int]:
    condition = src.readline().strip()
    if condition != 'sat':
        raise ValueError("Not satisfiable")
    model = sexpdata.load(src)
    model = strip_symbols(model)
    if model[0] != 'model':
        raise ValueError("Top-level element is not a model")
    definitions: Dict[str, int] = {}
    for definition in model[1:]:
        if definition[0] != 'define-fun':
            continue
        name = definition[1]
        value = definition[4]
        definitions[name] = value
    values: Dict[Definition, int] = {
        Definition.from_name(x): y
        for x, y in definitions.items()
    }
    return values


def main():
    solution = parse_solution(sys.stdin)
    num_rounds = max(x.round for x in solution.keys())
    num_zones = max(x.zone for x in solution.keys())
    num_matches_per_round = max(x.match for x in solution.keys())
    num_teams = max(x for x in solution.values())
    for round in range(1, num_rounds + 1):
        for match in range(1, num_matches_per_round + 1):
            print(",".join(
                str(solution[Definition(round, match, zone)])
                for zone in range(1, num_zones + 1)
            ))


if __name__ == '__main__':
    main()
