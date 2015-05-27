#!/usr/bin/python2

import sys
import numpy

### Function Definitions ###
def help():
    print("""Usage: pynabe-sugano.py -d [electrons] -v1 [wavenumber] -v2 [wavenumber] -t [high-energy-excited-state]-[low-energy-excited-state]
Example:
    ./pynabe-sugano.py -d 6 -v1 467 -v2 333 --use-nm -t 1T2g-1T1g
Parameters:
    -d      Number of d electrons in the complex (determines what diagram to use)
    -v1     Lower energy peak value in cm^-1 (can take wavelenght if --use-nm is used)
    -v2     Higher energy peak value in cm^-1 (can take wavelenght if --use-nm is used)
    -t      Specify what are the excited states of the desired transitions, separated by a '-'
Options:
    --help, -h          Display this and quit
    --about             Display about message and quit
    --use-nm            Take wavelenght in nm for v1 and v2 inputs
    --list-states, -ls  used with -d [electrons] to list what are the states for that diagram
    --quiet, -q         Don't print input options, only results
""")
    
def about():
    print("Python script that automates calculations involving Tanabe-Sugano diagrams \nThe task of finding the ratio of the heights of two lines with a ruler and then determining the x and y intercepts in Tanabe-Sugano diagrams is tedious and slow. This script utilizes 'diagrams' in the form of tables and searches for the ratio automatically and then calculates the B Racah parameter and 10Dq.")
    
def get_diagram(d_electrons):
    path='diagrams/'
    filename='d'+str(d_electrons)+'.csv'
    table=path+filename
    diagram = numpy.genfromtxt(table, names=True)
    return diagram
    
def list_states(diagram):
    print(diagram.dtype.names[1::])
    
def find_transition(diagram, transition):
    index = 1
    state1 = ''
    state2 = ''
    for state in diagram.dtype.names[1::]:
        if state.lower() == transition[0].lower():
            state1 = index
        if state.lower() == transition[1].lower():
            state2 = index
        index += 1
    transition=[state1, state2]
    return transition
    
def allowed_transitions(diagram):
    # To be done!
    pass
     
def parse_transition(transition):
    state1=[]
    state2=[]
    chars=list(transition)
    for i in range(len(chars)):
        if chars[i] == '-':
            state1 = state1 + chars[:i:]
            state2 = state2 + chars[i+1::]
            break
    if state1[0] == state2[0]:
        parity=True
    else:
        parity=False

    transition=[(''.join(state1)), (''.join(state2))]
    return transition, parity
    
def deltaOctB(ratio, diagram, columns):
    delta_list = [diagram[i][0] for i in range(len(diagram))]
    e_states = [diagram[e][columns[0]] for e in range(len(delta_list))]
    g_states = [diagram[g][columns[1]] for g in range(len(delta_list))]
    
    h2B = []
    h2B_o = []    
    h1B = []
    h1B_o = []
    Ev1_B = []
    Ev2_B = []
    y = []
    yo = []
    x = []
    xo = []
    delta_B = []

    current_ratio = 0
    index = 0
    for delta in delta_list:
        previous_ratio = current_ratio
        if g_states[index] != 0:
            current_ratio = e_states[index]/g_states[index]
        else:
            current_ratio = 0
        
        if index > 0:
            previous_delta = delta_list[index-1]
        else:
            previous_delta = delta
        
        if (ratio < current_ratio and ratio > previous_ratio) or (ratio > current_ratio and ratio < previous_ratio):
            x += [delta]
            xo += [previous_delta]
            y += [current_ratio]
            yo += [previous_ratio]
            h2B += [e_states[index]]
            h2B_o += [e_states[index-1]]
            h1B += [g_states[index]]
            h1B_o += [g_states[index-1]]
        index += 1

    for i in range(len(x)):
        m_ratio = (y[i]-yo[i])/(x[i]-xo[i])
        delta_B += [(((ratio - yo[i])/m_ratio) + xo[i])]
        m_h2 = (h2B[i]-h2B_o[i])/(x[i]-xo[i])
        m_h1 = (h1B[i]-h1B_o[i])/(x[i]-xo[i])
        Ev2_B += [((m_h2*(delta_B[i]-xo[i]))+h2B_o[i])]
        Ev1_B += [((m_h1*(delta_B[i]-xo[i]))+h1B_o[i])]
        
    return delta_B, Ev1_B, Ev2_B
             
def options():
    print_options = True
    verbose = False
    use_file = False    
    
    use_nm = False
    v1=0
    v2=0
    d_electrons=''
    transition=''
    
    for arg in range(len(sys.argv)):
    
        opt = sys.argv[arg]
        # using the next arg (if inside range) in the command as
        # the current 'opt' value
        if arg < len(sys.argv)-1:
            val = sys.argv[arg+1]
        else:
            val = 0
        
        if opt == "-d":
            d_electrons = val
        if opt == "--list-states" or opt == "-ls":
            list_states(get_diagram(d_electrons))
            sys.exit(0)
        if opt == "-v1":
            v1 = val
        if opt == "-v2":
            v2 = val
        if opt == "-t" or opt == "--transition":
            transition=val
        if opt == "--use-nm":
            use_nm = True
        if opt == "--use-file":
            use_file = True
        
        
        if opt == "-h" or arg == "--help":
            help()
            sys.exit(0)
        if opt == "--about":
            about()
            sys.exit(0)
        if opt == "--quiet" or opt == "-q":
            print_options = False
        if opt == "--verbose":
            verbose = True
    if ((not(use_file)) and d_electrons and v1 and v2):
        d_electrons=int(d_electrons)
        v1=float(v1)
        v2=float(v2)
        if use_nm:
            Ev1 = round(((10**7)/v1), 3)
            Ev2 = round(((10**7)/v2), 3)
        else:
            Ev1 = v1
            Ev2 = v2
        if Ev1 > Ev2:
            a = Ev2
            Ev2 = Ev1
            Ev1 = a
        if transition != '':
            (transition_name, parity) = parse_transition(transition)
            transition_string = "Transition %s <- %s " % (transition_name[0], transition_name[1])
            if parity:
                transition_string = transition_string + "is spin-allowed."
            else:
                transition_string = transition_string + "is spin-forbidden."
      
        else:
            #transition_string = "Transition not specified, assuming spin-allowed transitions from ground state."
            # to be implemented: allowed_transitions(diagram)
            help()
            sys.exit(0)
        if print_options:
            print ("Using diagram for d%s complex" % d_electrons)
            print("Ev1 wavenumber is %s cm^-1" % Ev1)
            print("Ev2 wavenumber is %s cm^-1" % Ev2)
            print("Ev2/Ev1 ratio is %s" % round((Ev2/Ev1), 3))
            #print transition_string

    else:
        help()
        sys.exit(0)      
            
    opts = (Ev1, Ev2, d_electrons, transition, verbose)
    return opts
    
### Entry point ###
opts = options()
Ev1 = opts[0]
Ev2 = opts[1]
d_electrons = opts[2]
transition = opts [3]
ratio = Ev2/Ev1
diagram = get_diagram(d_electrons)
if transition != '':
    transition, parity = parse_transition(transition)

#else:
#    transition = allowed_transitions(diagram)
# implement allowed transitions checking!!

columns = find_transition(diagram, transition)
print("Calculating ...")
delta_B, Ev1_B, Ev2_B = deltaOctB(ratio, diagram, columns)
B=[]
E10Dq=[]
for i in range(len(delta_B)):
    B1 = Ev1/Ev1_B[i]
    B2 = Ev2/Ev2_B[i]
    B += [(B1+B2)/2]
    E10Dq += [(delta_B[i]*B[i])]

if len(E10Dq) != 2:
    if len(E10Dq) != 1:
        print("More than two matches found!")
        print("all %s matches:" % len(E10Dq))
    for i in E10Dq:
        if len(E10Dq) != 1:
            print("Match %s:" % (i+1))
        print("10Dq/B is %s" % round(delta_B[i], 2))
        print("Ev1/B is %s and Ev2/B is %s" % (round(Ev1_B[i], 2), round(Ev2_B[i], 2)))
        print("B Racah parameter is %s" % round(B[i], 2))
        print("10Dq is %s" % round(E10Dq[i], 2))
if len(E10Dq) == 2:
    print("Two matches found!\n")
    print("Weak field match:")
    print("10Dq/B is %s" % round(delta_B[0], 2))
    print("Ev1/B is %s and Ev2/B is %s" % (round(Ev1_B[0], 2), round(Ev2_B[0], 2)))
    print("B Racah parameter is %s" % round(B[0], 2))
    print("10Dq is %s \n" % round(E10Dq[0], 2))
    print("Strong field match:")
    print("10Dq/B is %s" % round(delta_B[1], 2))
    print("Ev1/B is %s and Ev2/B is %s" % (round(Ev1_B[1], 2), round(Ev2_B[1], 2)))
    print("B Racah parameter is %s" % round(B[1], 2))
    print("10Dq is %s" % round(E10Dq[1], 2))


