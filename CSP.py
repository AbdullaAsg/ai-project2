import heapq

class Queue:   
    def __init__(self):
        self.list = []

    def push(self, item):
        
        self.list.insert(0, item)

    def pop(self):
        
        return self.list.pop()

    def isEmpty(self):
        
        return len(self.list) == 0

class PriorityQueue: 
    def __init__(self):
        self.heap = []

    def push(self, item, priority):
        pair = (priority, item)
        heapq.heappush(self.heap, pair)

    def pop(self):
        (priority, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0


# Base class for all constraints
class Constraint(object):
    def __init__(self, variables):
        self.variables = variables

    
class CSP(object):
    #initializer creates the constraints dict and assigning variables to domains

    def __init__(self, variables, domains):
        
        self.variables = variables
        # domains = dictionary mapping variables to lists of constraints imposed to it.
        self.domains = domains
        # constraints = {}, dictionary of variable as key, and constrain implementation as value each constraion
        self.constraints = {}
        self.arcs = { "binarArc": []}
        
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain assigned to it.")

    
    def add_constraint(self, constraint):
        # constraint: Constraint[V, D]) -> None
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            else:
                self.constraints[variable].append(constraint)
        # also create an arc associating with the constrain variables.
        arc = constraint.variables
        

    # Check if the value assignment is consistent by checking all constraints for the given variable against it
    # assignment = given configuration of variables and selected domains that should statisfy the constrains.
    # function that checks every constraint for a given variable against an assignment to see if the variables value
    # in the assignment works for the constraints.
    def consistent(self, variable, assignment):
        
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True


   #kind of recursive depth-first search. 
    def fsearch(self):
        return self.fSearchDfs({})

    def fSearchDfs(self, assignment):

        unassigned = [v for v in self.variables if v not in assignment]

        #goal test
        if len(unassigned) == 0:
            return assignment

        #choose variable with MRV heuristic 
        chosen_variable = self.MRV(unassigned)
        
       # sort domain values by LCV heuristic
        sorted_domain = self.LCV(assignment, chosen_variable)

        for value in sorted_domain:
            assignment[chosen_variable] = value         # Here we assign value to a variable !
            if self.consistent(chosen_variable, assignment):        # if we're still consistent, we continue
                result = self.fSearchDfs(assignment)
                if result != None:
                    return result
            assignment.pop(chosen_variable, None)         # if we didn't find the result, we will end up backtracking without this option
        return None

    #AC-3 detects conflicts that you will have in attributions, during the backtracking, and deletes them
    def ac3(self):

        # creating the arcs queue
        queue = Queue()
        for arc in self.arcs["binarArc"]:
            queue.push(arc)

        # remove values from arcs domains till their are none to remove
        while not queue.isEmpty():
            x,y = queue.pop()
            if self.RemoveInconsistentValues(x,y):
               # Every time a value is removed from the domain, you'll have to recheck the neighbors of x.
               for arc in self.arcs:
                    if y not in arc:
                        queue.push(arc)

    # here we implement the value remove.
    def RemoveInconsistentValues(self, x,y):
        value_removed_flag = False
        temp_assignment = {}        # temp assigning to check constrain only!
        for x_value in self.domains[x]:
            is_consistent = False
            temp_assignment[x] = x_value
            for y_value in self.domains[y]:
                temp_assignment[y] = y_value
                if self.consistent(x, temp_assignment):
                    is_consistent = True
            if not is_consistent:
                self.domains[x].remove(x_value)
        return value_removed_flag

    def MRV(self, unassigned_variables):
        
        smallest_domain_variable = unassigned_variables[0]
        for variable in unassigned_variables:
            if len(self.domains[variable]) < len(self.domains[smallest_domain_variable]):
                smallest_domain_variable = variable
        return smallest_domain_variable

    def LCV(self, assignment, variable):
        # assignment = dictionary of {variable: domain list[] }

        new_domain =PriorityQueue()

        for value in self.domains[variable]:

            lcv_score = 0
            local_assignment = assignment.copy()
            # Here we assign value to a variable !
            local_assignment[variable] = value

            for constraint in self.constraints[variable]:
                if not constraint.satisfied(local_assignment):
                    lcv_score = lcv_score + 1
            # print lcv_score
            new_domain.push(value, lcv_score)

        # converting to a sorted list
        new_domain_as_list = []
        while not new_domain.isEmpty():
            new_domain_as_list.append(new_domain.pop())
        return new_domain_as_list

    def clear(self):
        self.variables = None
        self.domains = None
        self.constraints = None

# implementing framework constrain.
class MapColoringConstraint(Constraint):
    def __init__(self, variable_1, variable_2):
        super(MapColoringConstraint, self).__init__([variable_1, variable_2])
        self.variable_1 = variable_1
        self.variable_2 = variable_2

    # if not yet to be assigned they are not conflicting for sure.
    def satisfied(self, assignment):
        if self.variable_1 not in assignment or self.variable_2 not in assignment:
            return True

        # check if 2 adjust colors are not conflicting
        return assignment[self.variable_1] != assignment[self.variable_2]

def Coloringfunc(filename):
    #reading input file
    with open(filename) as f:
        lines = f.readlines()
    output=[]
    for line in lines:
        if not line.startswith('#'):
            line=line.replace('\n',"")
            output.append(line)
        
    color = output[0]
    splitresult = color.split("=",2)
    output=output[1:]
    From=[]
    To=[]
    for i in output:
        From.append((i.split(',',2)[0]))
        To.append((i.split(',',2)[1]))

    #variable set
    All=From+To
    variables=set(All)
    print ("\ntesting map coloring:\n")
    #domain set
    domains = {}
    col=["red", "green", "blue","black","violet","white","orange","yellow","grey","pink","brown","purple"]
    for variable in variables:
        domains[variable] =col[:int(splitresult[1])]

    csp_instance = CSP(variables, domains)
    #creating graph
    for i in range(len(From)):
        csp_instance.add_constraint(MapColoringConstraint(From[i], To[i]))

    for index in range(5):
        csp_instance.ac3()
  
    solution = csp_instance.fsearch()
    if solution is None:
        print ("No solution found!")
    else:
        print ("\nSolution found:\n", solution)


#testing
f=input("Enter filename:")
Coloringfunc(f)




















    
