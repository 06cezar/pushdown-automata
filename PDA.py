# push down automaton
class PDAError(Exception): # exception is a class that all built-in Python errors (like ValueError, TypeError) inherit from.
    pass                   # defining a custom error that behaves like a normal Python exception with subclasses that 
                           # help categorize different types of PDA errors

class UndefinedStartStateError(PDAError):
    # raised when the PDA doesn't have a start state
    pass

class UndefinedAcceptStatesError(PDAError):
    # raised when the PDA doesn't have any accept states
    pass

class UndefinedAlphabetError(PDAError):
    # raised when the PDA doesn't have an alphabet
    pass
class InvalidStateError(PDAError):
    # raised when an invalid/undefined state is encountered.
    pass

class InvalidSymbolError(PDAError):
    # raised when an invalid/undefined symbol is encountered.
    pass

class EpsilonTransitionError(PDAError):
    # raised when you find
    pass 

class InputStringError(Exception):
    # raised when there isn't an error with the PDA, but with the input string fed into it (it contains characters not present in the PDA's alphabet)
    pass

# duplicate rule error seen in PDA's no longer found - the PDA transition function allow for multiple destination states for the same source state and symbol

def isComment(string):
    return string.startswith("#")
    # return string[0] == "#" would raise an IndexError for an empty string ""

def stringWithoutComments(string):
    return string[0 : string.index("#")] # does not raise an exception, as function is only called 
                                         # when character "#" exists in the string, and everything after
                                         # the first "#" shouldn't be processed
def isEmptyLine(string):
    return string == ""

def fixUtf8Corruption(possiblyCorruptedString):
    try:
        # attempt to fix the corrupted string:
        # 1. first, interpret the string as if it were encoded in Latin-1 (a single-byte encoding).
        # 2. then, decode it properly as UTF-8 (which may fix misinterpreted characters).
        # example: 'Îµ' (Windows-1252 corruption) should become 'ε' (UTF-8 character).
        return possiblyCorruptedString.encode("latin1").decode("utf-8") 
        # if any error is found exception will be caught and return clause will not be triggered
    
    except (UnicodeEncodeError, UnicodeDecodeError):
        # if either encoding or decoding fails:
        # - an UnicodeEncodeError could occur if the string can't be encoded to Latin-1.
        # - an UnicodeDecodeError could occur if the byte sequence can't be decoded to UTF-8.
        # in either case, the string is returned as it is (uncorrupted or irreparably corrupted).
        return possiblyCorruptedString  # return the original string if no fix was possible

def parseFile(inputPDAFile):
    lines = inputPDAFile.readlines()
    currentSection = "None"
    states = []
    sigma = [] # sigma = alphabet
    stackSigma = []
    rules = {} # rules[sourceState] = {symbol : destinationState}
               # tules[sourceState][symbol] = destinationState
    start = "None" # a PDA can only have one start state
    accept = [] # a PDA can have multiple accept states
    inMultipleLineComment = False # boolean variable to allow multiple line comments starting with /* and ending with */
                               # is true if we are currently inside a multi line comment and we need to skip all lines until */
    for line in lines:
        line = line.strip() # eliminating whitespace
        
        # continue statements go to next iteration (next line) and are used for readability purposes,
        # could be replaced by elif statements
        
        if isComment(line) or isEmptyLine(line):
            continue # skipping lines that are comments
            
        if "#" in line: # filtering lines that contain comments
            line = stringWithoutComments(line) # only text before the comment is processed 
            line = line.strip() # eliminating possible whitespace before first "#" character
            
        if not inMultipleLineComment:
            
            if "/*" in line:
                
                inMultipleLineComment = True # we are inside a multiple line comment
                # even though we are now in a multiple line comment, it can still be used as a one-liner
                # and this needs to be checked
                multipleLineCommentStartIndex = line.find("/*") # gives the position of the first comment opener
                
                if "*/" in line:

                    multipleLineCommentLastStartIndex = line.rfind("/*") # more /* can be used in a line, checks for the last one
                    multipleLineCommentLastEndIndex = line.rfind("*/") # gives the position of the last ending comment symbol
                    
                    if multipleLineCommentLastStartIndex < multipleLineCommentLastEndIndex:
                        # then this is actually a one liner comment
                        inMultipleLineComment = False
                        line = line[:multipleLineCommentStartIndex] + line[multipleLineCommentLastEndIndex + 2:] # concatenates string before the comment and after the comment
                        line = line.strip()
                        # checks if there is anything to parse before and after the comment
                        
                else:   # not a one-liner comment - only need to check before the /* 
                    
                    line = line[:multipleLineCommentStartIndex] # checks if there is anything to parse before the comment
                    line = line.strip()
                    
                if isEmptyLine(line):
                    continue
            
            
            
        elif inMultipleLineComment: # this means that it's not the first line in the comment
                                    # elif statement ensures that the parser won't skip lines that are before the start of a multiple line comment
                                    # for example, q1, 1, q0 /* some text - would be skipped by the continue statement if not for the elif statement
            if "*/" in line:
                
                multipleLineCommentEndIndex = line.rfind("*/")
                line = line[multipleLineCommentEndIndex + 2:] # the string after the */ (is not a comment)
                inMultipleLineComment = False
                line = line.strip()
                if isEmptyLine(line):
                    continue
                
            else:
                continue # skip line that is completely within the multiple line comment
        
        if line[0] == "[": # new section starts here, filtering opening and closing pharantesis
            currentSection = line[1:-1]
            continue
        if line == "End":
            currentSection = "None" # searching for new section tag ([SectionName])
            continue
        
        if currentSection == "None":
            continue # skipping line, still searching for section tags ([SectionName])
        if currentSection == "States":
            states.append(line) 
            continue
        if currentSection == "Sigma":
            sigma.append(line)
            continue 
        if currentSection == "Stack Sigma":
            stackSigma.append(line)
        if currentSection == "Rules":
            sourceState, symbol, popSymbol, pushSymbol, destinationState = line.split(",")
            sourceState = fixUtf8Corruption(sourceState)
            sourceState = sourceState.strip()
            symbol = symbol.strip() 
            symbol = fixUtf8Corruption(symbol) # fixing any possible corruption that can be caused by file in different encoding from utf-8
            popSymbol = popSymbol.strip() 
            popSymbol = fixUtf8Corruption(popSymbol) # fixing any possible corruption that can be caused by file in different encoding from utf-8
            pushSymbol = pushSymbol.strip() 
            pushSymbol = fixUtf8Corruption(pushSymbol) # fixing any possible corruption that can be caused by file in different encoding from utf-8
            destinationState = fixUtf8Corruption(destinationState)
            destinationState = destinationState.strip()
            if sourceState not in rules:        
                rules[sourceState] = {} # initialising with a hashmap
                
                                        # a transition function 
                                        # δ  :  Q    ×   Σ   x   stΣ   x   stΣ        →  P(Q)
                                        #     srcSt    symbol  popSymbol  pushSymbol   destStates
            if symbol == "ε" or symbol.lower() == "epsilon":
                symbol = "epsilon" # will be the symbol present in the dictionary for all epsilon transitions
                                   # ε looks prettier and more formal - but some older text editors without UTF-8 or 
                                   # with weirder font styles may not display it correctly
                                   # or make it too similar with an 'e'
                                                                                             
            if symbol not in rules[sourceState]:
                rules[sourceState][symbol] = {}
    
            if popSymbol == "ε" or popSymbol.lower() == "epsilon":
                popSymbol = "epsilon"
            
            rules[sourceState][symbol][popSymbol] = {} 

            if pushSymbol == "ε" or pushSymbol.lower() == "epsilon":
                pushSymbol = "epsilon"

            rules[sourceState][symbol][popSymbol] = {
                "push" : pushSymbol,
                "nextState" : destinationState
            }

        if currentSection == "Start":
            start = line
            continue
        if currentSection == "Accept":
            accept.append(line)
            continue

    inputPDAFile.close()
    
    PDA = states, sigma, stackSigma, rules, start, accept
    printPDADataStructures(PDA)
    if not isPDAValid(PDA):
        return False 
    else:
        # returning 5-tuple
        return PDA
    
def isEmpty(stack):
    return not bool(stack) 

def top(stack):
    return stack[-1]

def isPDAValid(PDA):
    states, sigma, stackSigma, rules, start, accept = PDA
    if len(sigma) == 0:
        raise UndefinedAlphabetError("Alphabet is not defined")
        return False
    
    if len(stackSigma) == 0:
        raise UndefinedAlphabetError("Stack alphabet is not defined")
        return False 
    
    if start == "None":
        raise UndefinedStartStateError("Start state is not defined")
        return False 
    
    elif start not in states:
        raise InvalidStateError(f"Start state {start} is not defined")
        return False
    
    if len(accept) == 0:
        raise UndefinedAcceptStatesError("Accept state is not defined")
        return False 
    
    else:
        for acceptState in accept:
            if acceptState not in states:
                raise InvalidStateError(f"Accept state {acceptState} is not defined")
                return False
            
            
    for sourceState in rules: # rules dict key is the source state of the rule
        # print(sourceState)
        if sourceState not in states:
            raise InvalidStateError(f"Source state {sourceState} is not defined in the states list for the PDA")
            return False
        
        for symbol in rules[sourceState]:
            # print(symbol)
            if symbol not in sigma and symbol not in ["epsilon", "ε"]: # epsilon doesn't need to be defined in the alphabet
                raise InvalidSymbolError(f"Symbol {symbol} is not defined in the alphabet for the PDA")
                return False
            elif symbol in ["epsilon", "ε"] and symbol in sigma:
                raise EpsilonTransitionError("Epsilon doesn't need to be defined in the alphabet for the PDA (it includes it by default). You can use 'epsilon' or 'ε' in your rules without defining epsilon or ε.")
            
            for popSymbol in rules[sourceState][symbol]:
                if popSymbol not in stackSigma and popSymbol not in ["epsilon", "ε"]: # epsilon doesn't need to be defined in the alphabet
                    raise InvalidSymbolError(f"Symbol {popSymbol} is not defined in the stack alphabet for the PDA")
                    return False
                elif symbol in ["epsilon", "ε"] and symbol in sigma:
                    raise EpsilonTransitionError("Epsilon doesn't need to be defined in the stack alphabet for the PDA (it includes it by default). You can use 'epsilon' or 'ε' in your rules without defining epsilon or ε.")
            # for destinationState in rules[sourceState][symbol]: not for, as there is only one destinationState, this for would split the destinationState
            # string character by character

                pushSymbol = rules[sourceState][symbol][popSymbol]["push"]
                if pushSymbol not in stackSigma and pushSymbol not in ["epsilon", "ε"]: # epsilon doesn't need to be defined in the alphabet
                    raise InvalidSymbolError(f"Symbol {pushSymbol} is not defined in the stack alphabet for the PDA")
                    return False
                elif pushSymbol in ["epsilon", "ε"] and pushSymbol in stackSigma:
                    raise EpsilonTransitionError("Epsilon doesn't need to be defined in the stack alphabet for the PDA (it includes it by default). You can use 'epsilon' or 'ε' in your rules without defining epsilon or ε.")
                destinationState = rules[sourceState][symbol][popSymbol]["nextState"]
                if destinationState not in states:
                        raise InvalidStateError(f"Destination state {destinationState} is not defined in the states list for the PDA")                            # print(sourceState, symbol, destinationState)
                        return False
                        # traverses all rules in the dictionary, looking for source states, destination states and symbols
    return True

def printPDADataStructures(PDA):
    states, sigma, stackSigma, rules, start, accept = PDA # getting values from 5-tuple

    print(f"States : {states}")
    print(f"Alphabet : {sigma}")
    print(f"Stack Alphabet: {stackSigma}")
    print(f"Rules : {rules}")
    print(f"Start state : {start}")

    if len(accept) != 1:
        print(f"Accept states : {accept}") 
    else:
        print(f"Accept state: {accept[0]}") # to show singular form if needed and not a list with only one element

def isStringValid(string, stringSeparator, sigma):
    # searches if any element in the string is not included in the alphabet
    for symbol in splitIncludingNoSeparator(string, stringSeparator):
        if symbol not in sigma:
            return False
    return True

def getNextState(currentState, currentSymbol, rules, stack):
    if currentState not in rules:
        return currentState # considered by default for every state, if a rule is not specified, the pda stays in the same state
                            # here we have no rule with the source state = the current state of the pda
    elif currentSymbol not in rules[currentState]:
        return currentState # same case, but in the PDA we have a rule defined with the current state as the source state
                            # but no rule with the corresponding symbol, so we stay in the same state (by convention)
    elif "epsilon" not in rules[currentState][currentSymbol]:
        if isEmpty(stack):
            return currentState
        elif top(stack) not in rules[currentState][currentSymbol]:
            return currentState
        else:
            pushSymbol = rules[currentState][currentSymbol][top(stack)] ["push"]
            oldStackTop = top(stack)
            stack.pop()
            if pushSymbol != "epsilon":
                stack.append(pushSymbol)
            destinationState = rules[currentState][currentSymbol][oldStackTop]["nextState"]
            return destinationState
    else: # rules[currentState][currentSymbol] == "epsilon"
        pushSymbol = rules[currentState][currentSymbol]["epsilon"]["push"]
        if pushSymbol != "epsilon":
            stack.append(pushSymbol)
        destinationState = rules[currentState][currentSymbol]["epsilon"]["nextState"]
        return destinationState
    
        
    
def splitIncludingNoSeparator(string, separator):
    if separator == "" : # if not for this function, ValueError: empty separator
        return string  # would need an if-else statement within the runPDA function
    else:                # removes redudant code, by calling getNextState only once
        return string.split(separator)
    
def epsilonClosure(currentState, rules, stack):
    if currentState not in rules:
        return currentState
    if "epsilon" in rules[currentState]:
        if isEmpty(stack):
            if "epsilon" in rules[currentState]["epsilon"]:
                pushSymbol = rules[currentState]["epsilon"]["epsilon"]["push"]
                if pushSymbol != "epsilon":
                    stack.append(pushSymbol)
                currentState = rules[currentState]["epsilon"]["epsilon"]["nextState"]
        else:
            if top(stack) in rules[currentState]["epsilon"]:
                oldStackTop = top(stack)
                stack.pop()
                pushSymbol = rules[currentState]["epsilon"][oldStackTop]["push"]
                if pushSymbol != "epsilon":
                    stack.append(pushSymbol)
                currentState = rules[currentState]["epsilon"][oldStackTop]["nextState"]
            elif "epsilon" in rules[currentState]["epsilon"]:
                pushSymbol = rules[currentState]["epsilon"]["epsilon"]["push"]
                if pushSymbol != "epsilon":
                    stack.append(pushSymbol)
                currentState = rules[currentState]["epsilon"]["epsilon"]["nextState"]

    return currentState


def runPDA(PDA, inputString, stringSeparator, printPDASteps = True):

    states, sigma, stackSigma, rules, start, accept = PDA # getting values from 5-tuple
    stack = []
    # could check if the PDA is valid before running it, but the runPDA function should return an error
    # string instead of just False, because False might be misinterpreted as last state of the PDA is not
    # an accept state
    # but PDA validity is also looked upon when processing the file
    # if the functions are arranged in different files/modules, code like this is preferrable
    if not isPDAValid(PDA):
        raise PDAError("PDA not valid")
    
    inputString = inputString.strip() # removes whitespace, \n, from left and right
    if not isStringValid(inputString, stringSeparator, sigma):
        raise InputStringError("Input string contains symbols not in the given alphabet of the PDA")
    
    currentState = start # first state is the start state of the PDA
    if printPDASteps == True: 
        # printPDASteps - boolean parameter - if it is true all the states and symbols the PDA encounters
        # will be printed to the screen - if not, only if the input string is valid will be printed to the screen
        print(currentState) # printing starting state

    currentState = epsilonClosure(currentState, rules, stack)

    for currentSymbol in splitIncludingNoSeparator(inputString, stringSeparator):
            if printPDASteps == True:
                print(currentSymbol) # printing every symbol in the string
            
            currentState = getNextState(currentState, currentSymbol, rules, stack) 
            # function searches through the rules and finds the correct one 
            # improved time efficiency wise by using two hashmaps - dictionaries, for O(1) search time
 
            if printPDASteps == True:
                print(currentState)  # printing the new state of the PDA after every symbol

    stateBeforeEpsilon = currentState
    currentState = epsilonClosure(currentState, rules, stack)
    if stateBeforeEpsilon != currentState and printPDASteps == True:
        print(currentState)
    if currentState in accept: # after the for loop exits the currentState variable stores the last state 
        return True            # of the PDA, if it is valid return true
    else:
        return False
    
        
        