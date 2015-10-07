#!/usr/bin/python2
###############################################################################
#
#   Pynabe-sugano is a calculator for Tanabe-Sugano diagrams.
#   Copyright 2015 Ricardo B. Ayres
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import sys
import json

### Function Definitions ###
def help():
    print("""Usage: pynabe-sugano.py -d [electrons] -v1 [wavenumber] [excited state]-[ground state] -v2 [wavenumber] [excited state]-[ground state]
Example:
    ./pynabe-sugano.py -d 6 -v1 467 1t1g-1a1g -v2 333 1t2g-1a1g --use-nm

Parameters:
    -d      Number of d electrons in the complex (determines what diagram to use)
    -v1     Lower energy peak value in cm^-1 followed by the transition. (can take wavelenght if --use-nm is used)
    -v2     Higher energy peak value in cm^-1 followed by the transition. (can take wavelenght if --use-nm is used)
    Transitions are specified with the excited state followed by the ground state and separated by a '-'. See example above.

Options:
    --help, -h          Display this and quit
    --about             Display about message and quit
    --use-nm            Take wavelenght in nm for v1 and v2 inputs
    --list-states, -ls  used with -d (i.e. -d 2 -ls) to list what are the states for that diagram
    --quiet, -q         Don't print input options, only results
""")
    sys.exit(0)
    
def about():
    print("""
    Pynabe-sugano is a calculator for Tanabe-Sugano diagrams.    
    Pynabe-sugano  Copyright (C) 2015  Ricardo B. Ayres
    
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
""")
    sys.exit(0)
    
def get_diagram(d_electrons):
    path='diagrams/'
    filename='d'+str(d_electrons)+'.json'
    table=open(path+filename, 'r')
    diagram = json.load(table)
    table.close()
    return diagram
    
def list_states(diagram):
    states = list(diagram.keys())
    if 'deltaB' in states:
        states.remove('deltaB')
    print("Available states in this diagram are: ")
    for state in states:
        print(state),
    print("\n\nFor more information refer to:\nhttps://en.wikipedia.org/wiki/Tanabe%E2%80%93Sugano_diagram#Tanabe-Sugano_diagrams")
    sys.exit(0)
    
def allowed_transitions(diagram):
    # To be done!
    pass
     
def parse_transition(diagram, transition):
    g_state=[]
    e_state=[]
    chars=list(transition)
    for i in range(len(chars)):
        if chars[i] == '-':
            e_state = e_state + chars[:i:]
            g_state = g_state + chars[i+1::]
            break
    if g_state[0] == e_state[0]:
        parity=True
    else:
        parity=False
    g_state = ''.join(g_state)
    e_state = ''.join(e_state)
    found_g, found_e = False, False
    for state in list(diagram.keys()):
        if g_state.lower() == state.lower():
            g_state = state
            found_g = True
        if e_state.lower() == state.lower():
            e_state = state
            found_e = True
    if found_g and found_e:
        transition=[e_state, g_state]
        return transition, parity
    else:
        print("Transition not found!")
        print("Use -d [electrons] -ls to list transitions.")
        print("Aborting.")
        sys.exit(0)
    
def deltaOctB(ratio, diagram, tv1, tv2):
    global verbose
    delta_list = diagram['deltaB']
    e2_state = diagram[tv2[0]]
    e1_state = diagram[tv1[0]]
    ground_state = diagram[tv1[1]]
      
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
        if e1_state[index] != 0:
            current_ratio = e2_state[index]/e1_state[index]
        else:
            current_ratio = 0
        
        if index > 0:
            previous_delta = delta_list[index-1]
        else:
            previous_delta = delta
        
        if verbose == 2:
            if index == 0:
                print("Searching for interval that contains Ev2/Ev1 = %s" % round(ratio, 3))
            print("[%.3f , %.3f]" % (round(previous_ratio, 3), round(current_ratio, 3))),
        if verbose == 2 and ground_state[index] != 0:
            print("<-- Ground state is not zero, skipping."),
            
        if ((ratio < current_ratio and ratio > previous_ratio) or (ratio > current_ratio and ratio < previous_ratio)) and (ground_state[index] == 0):
            if verbose == 2:
                print("<-- Found!"),
            x += [delta]
            xo += [previous_delta]
            y += [current_ratio]
            yo += [previous_ratio]
            h2B += [e2_state[index]]
            h2B_o += [e2_state[index-1]]
            h1B += [e1_state[index]]
            h1B_o += [e1_state[index-1]]
        if verbose == 2:
            print("")
        index += 1

    for i in range(len(x)):
        if verbose == 2:
            print("Interpolating from (%.3f , %.3f to (%.3f , %.3f)..." %
                (round(xo[i], 3), round(yo[i], 3), round(x[i], 3), round(y[i], 3)))
        m_ratio = (y[i]-yo[i])/(x[i]-xo[i])
        delta_B += [(((ratio - yo[i])/m_ratio) + xo[i])]
        m_h2 = (h2B[i]-h2B_o[i])/(x[i]-xo[i])
        m_h1 = (h1B[i]-h1B_o[i])/(x[i]-xo[i])
        Ev2_B += [((m_h2*(delta_B[i]-xo[i]))+h2B_o[i])]
        Ev1_B += [((m_h1*(delta_B[i]-xo[i]))+h1B_o[i])]
        
    return delta_B, Ev1_B, Ev2_B
    
### Entry Point ###
verbose = 1
use_file = False
use_nm = False
v1=0
v2=0
tv1=0
tv2=0
d_electrons=''

for arg in range(len(sys.argv)):

    opt = sys.argv[arg]
    # using the next arg (if inside range) in the command as
    # the current 'opt' value
    if arg < len(sys.argv)-1:
        val = sys.argv[arg+1]
    if arg < len(sys.argv)-2:
        val2 = sys.argv[arg+2]
    else:
        val = 0
        val2 = 0
    
    if opt == "-d":
        
        if val not in str(range(2,9)):
            print("Are you sure you need this?\nSee this and try again:\nhttps://en.wikipedia.org/wiki/Tanabe%E2%80%93Sugano_diagram#Unnecessary_diagrams:_d1.2C_d9_and_d10")
            sys.exit(0)
        
        else:
            d_electrons = val
        if val2 == "--list-states" or val2 == "-ls":
            list_states(get_diagram(d_electrons))
    
    if opt == "-v1":
        v1 = val
        tv1 = val2
    if opt == "-v2":
        v2 = val
        tv2 = val2
    if opt == "--use-nm":
        use_nm = True
    if opt == "--use-file":
        use_file = True
    if opt == "-h" or opt == "--help":
        help()
    if opt == "--about":
        about()
    if opt == "--quiet" or opt == "-q":
        verbose = 0
    if opt == "--verbose":
        verbose = 2

if d_electrons and v1 and v2 and tv1 and tv2:
    d_electrons = int(d_electrons)
    diagram = get_diagram(d_electrons)
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
    tv1, p1 = parse_transition(diagram, tv1)
    if p1:
        p1 = "spin-allowed."
    else:
        p1 = "spin-forbidden."
    
    tv2, p2 = parse_transition(diagram, tv2)
    if p2:
        p2 = "spin-allowed."
    else:
        p2 = "spin-forbidden."
    if tv1[1] != tv2[1]:
        print("Ground states are not the same. Aborting.")
        sys.exit(0)
    
    if verbose:
        print ("Using diagram for d%s complex" % d_electrons)
        print("Ev1 wavenumber is %.2f cm^-1" % Ev1)
        print("Ev2 wavenumber is %.2f cm^-1" % Ev2)
        print("Transition %s<-%s is %s" % (tv1[0], tv1[1], p1))
        print("Transition %s<-%s is %s" % (tv2[0], tv2[1], p2))
        print("Ev2/Ev1 ratio is %.3f" % round((Ev2/Ev1), 3))
else:
    help()
    sys.exit(0)

ratio = Ev2/Ev1
if verbose:
    print("Calculating ...")

delta_B, Ev1_B, Ev2_B = deltaOctB(ratio, diagram, tv1, tv2)
B=[]
E10Dq=[]
for i in range(len(delta_B)):
    B1 = Ev1/Ev1_B[i]
    B2 = Ev2/Ev2_B[i]
    B += [(B1+B2)/2]
    E10Dq += [(delta_B[i]*B[i])]

if len(E10Dq) == 0:
    print("No matches found! Ratio might be out of diagram range. Use --verbose for more information.")
    sys.exit(0)

if len(E10Dq) != 1:
    print("More than one match found!")
    print("Printing all %s matches:" % len(E10Dq))

for i in range(len(E10Dq)):
    if len(E10Dq) != 1:
        print("Match %s:" % (i+1))
    print("10Dq/B is %.2f" % round(delta_B[i], 2))
    print("Ev1/B is %.2f and Ev2/B is %.2f" % (round(Ev1_B[i], 2), round(Ev2_B[i], 2)))
    print("B Racah parameter is %.2f" % round(B[i], 2))
    print("10Dq is %.2f" % round(E10Dq[i], 2))


