import csv
import sys
import collections

allocation = list(csv.reader(sys.stdin))

teams = {
    team
    for match in allocation
    for team in match
}

print("\t" + "\t".join(sorted(teams)))

for team in sorted(teams):
    facing = collections.Counter(
        other_team
        for match in allocation
        for other_team in match
        if team in match
        if other_team != team
    )
    print(team + "\t" + "\t".join((str(facing[x]) if x != team else '-') for x in sorted(teams)))
