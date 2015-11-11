
f = open('')

header_ids_
for line in f:
	tokens = line.split()
	if len(tokens) != 2:
		raise ValueError("This file is not as expected, should have 2 tokens per line, and has: " + str(tokens))
	header_id = tokens[0]
	irods_id = tokens[1]




