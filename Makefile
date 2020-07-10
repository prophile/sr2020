all: show-facing final.csv

final.csv: initial.csv rezone.py
	python3 rezone.py <initial.csv >final.csv

initial.csv: probout.out parse_problem.py
	python3 parse_problem.py <probout.out >initial.csv

probout.out: probdef.z3
	z3 probdef.z3 > probout.out

probdef.z3: generate_problem.py
	python3 generate_problem.py > probdef.z3

show-facing: initial.csv
	python3 show_facing.py < initial.csv

clean:
	rm -rf probdef.z3 probout.out initial.csv final.csv

.PHONY: all clean show-facing
