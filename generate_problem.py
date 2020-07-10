# BEES

import sys
from typing import IO
from dataclasses import dataclass

@dataclass(frozen=True)
class Definition:
    num_rounds: int
    zones_per_match: int
    matches_per_round: int
    num_teams: int
    all_vs_all: int
    max_overlap: int

def generate_problem(out: IO[str], definition: Definition) -> None:
    # Declare all the variables
    for round in range(1, definition.num_rounds + 1):
        for match in range(1, definition.matches_per_round + 1):
            for zone in range(1, definition.zones_per_match + 1):
                out.write(f"(declare-const r{round}m{match}z{zone} Int)\n")
                out.write(f"(assert (>= r{round}m{match}z{zone} 1))\n")
                out.write(f"(assert (<= r{round}m{match}z{zone} {definition.num_teams}))\n")
                # Sequence constraints to reduce the search space; also ensures that the same
                # team is never scheduled twice in the same match.
                if zone > 1:
                    out.write(f"(assert (> r{round}m{match}z{zone} r{round}m{match}z{zone - 1}))\n")
        out.write("\n")
    # For each round, set the total number of team appearances
    appearances_per_team_per_round = (
        definition.matches_per_round *
        definition.zones_per_match //
        definition.num_teams
    )
    for round in range(1, definition.num_rounds + 1):
        for team in range(1, definition.num_teams + 1):
            out.write(f"(assert (= {appearances_per_team_per_round} (+\n")
            for match in range(1, definition.matches_per_round + 1):
                for zone in range(1, definition.zones_per_match + 1):
                    out.write(f"    (ite (= {team} r{round}m{match}z{zone}) 1 0)\n")
            out.write(")))\n")
        out.write("\n")

    if definition.all_vs_all == 1:
        # Implement the all vs all constraint
        for team in range(1, definition.num_teams):
            for other_team in range(team + 1, definition.num_teams + 1):
                out.write("(assert (or\n")
                for round in range(1, definition.num_rounds + 1):
                    for match in range(1, definition.matches_per_round + 1):
                        for zone_1 in range(1, definition.zones_per_match):
                            for zone_2 in range(zone_1 + 1, definition.zones_per_match + 1):
                                out.write( "    (and \n")
                                out.write(f"        (= r{round}m{match}z{zone_1} {team})\n")
                                out.write(f"        (= r{round}m{match}z{zone_2} {other_team})\n")
                                out.write( "    )\n")
                out.write("))\n")
        out.write("\n")
    elif definition.all_vs_all > 1:
        # Implement the all vs all constraint for facing everyone multiple times;
        # this is a slower code path than just requiring once since we need to sum
        # rather than or.
        for team in range(1, definition.num_teams):
            for other_team in range(team + 1, definition.num_teams + 1):
                out.write(f"(assert (<= {definition.all_vs_all} (+\n")
                for round in range(1, definition.num_rounds + 1):
                    for match in range(1, definition.matches_per_round + 1):
                        for zone_1 in range(1, definition.zones_per_match):
                            for zone_2 in range(zone_1 + 1, definition.zones_per_match + 1):
                                out.write( "    (ite (and \n")
                                out.write(f"        (= r{round}m{match}z{zone_1} {team})\n")
                                out.write(f"        (= r{round}m{match}z{zone_2} {other_team})\n")
                                out.write( "    ) 1 0)\n")
                out.write(")))\n")
        out.write("\n")

    # Compute overlap
    rounds_and_matches = [
        (round, match)
        for round in range(1, definition.num_rounds + 1)
        for match in range(1, definition.matches_per_round + 1)
    ]
    for n, (round_1, match_1) in enumerate(rounds_and_matches):
        for round_2, match_2 in rounds_and_matches[n + 1:]:
            out.write(f"(assert (>= {definition.max_overlap} (+")
            for zone_1 in range(1, definition.zones_per_match + 1):
                for zone_2 in range(1, definition.zones_per_match + 1):
                    out.write(f"(ite (= r{round_1}m{match_1}z{zone_1} r{round_2}m{match_2}z{zone_2}) 1 0)\n")
            out.write(")))\n")


    out.write("(check-sat)\n")
    out.write("(get-model)\n")


def main():
    defn = Definition(
        num_rounds=2,
        zones_per_match=4,
        matches_per_round=12,
        num_teams=12,
        all_vs_all=1,
        max_overlap=2,
    )
    generate_problem(sys.stdout, defn)


if __name__ == '__main__':
    main()
