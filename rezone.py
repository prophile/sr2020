import csv
import sys
import math
import copy
import collections
import statistics
import tqdm
import random
import itertools

reader = csv.reader(sys.stdin)
matches = list(reader)

NUM_ZONES = len(matches[0])
NUM_ITERATIONS = 1000
OPTIMAL_ENTROPY = math.log(NUM_ZONES, 2)

TEAMS = {
    team
    for match in matches
    for team in match
}

random.seed(1)

def get_appearances_by_zone(arrangement, selected_team):
    return collections.Counter(
        zone
        for match in matches
        for zone, team in enumerate(match)
        if team == selected_team
    )

def average_entropy(arrangement):
    entropies = []
    for selected_team in TEAMS:
        appearances_by_zone = get_appearances_by_zone(arrangement, selected_team)
        factor = 1 / sum(appearances_by_zone.values())
        entropies.append(-sum(
            x * factor * math.log(x * factor, 2)
            for x in appearances_by_zone.values()
        ))
    return statistics.mean(entropies)

for match in matches:
    random.shuffle(match)

best_entropy = average_entropy(matches)
best = copy.deepcopy(matches)

for n in tqdm.trange(NUM_ITERATIONS):
    temperature = math.exp(-10 * (n / NUM_ITERATIONS))
    new_entropy = average_entropy(matches)
    match_enumeration = list(enumerate(matches))
    random.shuffle(match_enumeration)
    for match_no, match in match_enumeration:
        if random.random() < temperature:
            random.shuffle(match)
        else:
            previous_best = list(match)
            for match_permutation in itertools.permutations(previous_best):
                match[:] = match_permutation
                modified_entropy = average_entropy(matches)
                if modified_entropy > new_entropy:
                    new_entropy = modified_entropy
                    previous_best = list(match_permutation)
            match[:] = previous_best
    new_entropy = average_entropy(matches)
    if new_entropy > best_entropy:
        best = copy.deepcopy(matches)
        best_entropy = new_entropy
    if best_entropy >= OPTIMAL_ENTROPY:
        break

print("Got to {:.3f}b of entropy (theoretical maximum is {:.3f}b)".format(
    best_entropy,
    OPTIMAL_ENTROPY,
), file=sys.stderr)

writer = csv.writer(sys.stdout)
for match in best:
    writer.writerow(match)

for team in sorted(TEAMS):
    print(team, ' / '.join(str(x) for x in sorted(get_appearances_by_zone(best, team).values(), reverse=True)), file=sys.stderr)
