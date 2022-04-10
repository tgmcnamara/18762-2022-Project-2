import numpy as np
def initialize(v_init, bus, generator, load, slack, transformer):

	for l in load:
		l.init_v(v_init, bus)
	
	for g in generator:
		g.init_v(v_init, bus)

	for s in slack:
		s.init_v(v_init, bus)

	for t in transformer:
		t.init_v(v_init, bus)

	return v_init
