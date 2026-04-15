from tabulate import tabulate
import tkinter as tk
from tkinter import filedialog

def getValues(userInput):
    """Determine truth values for variables p, q, and r based on user input."""
    p, q, r = [], [], []

    # Set truth values based on the presence of variables in the input
    if "p" in userInput and "q" in userInput and "r" in userInput:
        p = [0, 0, 0, 0, 1, 1, 1, 1]
        q = [0, 0, 1, 1, 0, 0, 1, 1]
        r = [0, 1, 0, 1, 0, 1, 0, 1]
    elif "p" in userInput and "q" in userInput:
        p = [0, 0, 1, 1]
        q = [0, 1, 0, 1]
    elif "p" in userInput and "r" in userInput:
        p = [0, 0, 1, 1]
        r = [0, 1, 0, 1]
    elif "q" in userInput and "r" in userInput:
        q = [0, 0, 1, 1]
        r = [0, 1, 0, 1]
    elif "p" in userInput:
        p = [0, 1]
    elif "q" in userInput:
        q = [0, 1]
    elif "r" in userInput:
        r = [0, 1]

    return p, q, r

def evalExpression(expression, p, q, r):
    """Evaluate a logical expression with given truth values for p, q, and r."""
    def applyOperator(op, left, right):
        """Apply logical operators (AND, OR, IMPLICATION, BICONDITIONAL) to the values."""
        if op == '^':
            return [int(l & r) for l, r in zip(left, right)]  # Logical AND
        elif op == 'v':
            return [int(l | r) for l, r in zip(left, right)]  # Logical OR
        elif op == '->':
            return [int(not l or r) for l, r in zip(left, right)]  # Logical IMPLICATION
        elif op == '<=>':
            return [int(l == r) for l, r in zip(left, right)]  # Logical BICONDITIONAL
        else:
            raise ValueError(f"Unsupported operator: {op}")

    precedence = {'~': 4, '^': 3, 'v': 2, '->': 1, '<=>': 0}
    stack = []  # To hold truth values during evaluation
    operators = []  # To hold operators encountered in the expression
    intermediateResults = {}  # To store results of intermediate expressions
    subExpressions = []  # To track sub-expressions for clarity
    i = 0  # Index for traversing the expression

    # Process the logical expression
    while i < len(expression):
        char = expression[i]
        if char in "pqr":
            # Push the respective truth values onto the stack
            if char == "p":
                stack.append(p)
                subExpressions.append("p")
            elif char == "q":
                stack.append(q)
                subExpressions.append("q")
            elif char == "r":
                stack.append(r)
                subExpressions.append("r")
        elif char == "~":
            # Handle negation
            i += 1
            if expression[i] == "(":
                # Negation of a sub-expression
                j = i + 1
                count = 1
                while count > 0:
                    if expression[j] == "(":
                        count += 1
                    elif expression[j] == ")":
                        count -= 1
                    j += 1
                subExpr = expression[i:j]
                subResult, subIntermediateResults = evalExpression(subExpr[1:-1], p, q, r)
                negation = [1 - x for x in subResult]  # Negate the result
                stack.append(negation)
                subExpressions.append("~" + subExpr)

                # Update intermediate results
                for key, value in subIntermediateResults.items():
                    intermediateResults[key] = value
                intermediateResults["~" + subExpr] = negation

                i = j - 1  # Move index past the processed sub-expression
            # Direct negation of variables p, q, or r
            elif expression[i] == 'p':
                negation = [1 - x for x in p]
                stack.append(negation)
                subExpressions.append("~p")
                intermediateResults["~p"] = negation
            elif expression[i] == 'q':
                negation = [1 - x for x in q]
                stack.append(negation)
                subExpressions.append("~q")
                intermediateResults["~q"] = negation
            elif expression[i] == 'r':
                negation = [1 - x for x in r]
                stack.append(negation)
                subExpressions.append("~r")
                intermediateResults["~r"] = negation
        elif char in "^v":
            # Handle binary operators (AND, OR)
            while (operators and operators[-1] != "(" and
                precedence[operators[-1]] >= precedence[char]):
                op = operators.pop()
                right = stack.pop()
                rightExpr = subExpressions.pop()
                left = stack.pop()
                leftExpr = subExpressions.pop()
                result = applyOperator(op, left, right)
                stack.append(result)
                newExpr = f"({leftExpr} {op} {rightExpr})"
                subExpressions.append(newExpr)
                intermediateResults[newExpr] = result
            operators.append(char)
        elif char == "-" and i + 1 < len(expression) and expression[i + 1] == ">":
            # Handle implication operator
            while (operators and operators[-1] != "(" and
                precedence[operators[-1]] >= precedence["->"]):
                op = operators.pop()
                right = stack.pop()
                rightExpr = subExpressions.pop()
                left = stack.pop()
                leftExpr = subExpressions.pop()
                result = applyOperator(op, left, right)
                stack.append(result)
                newExpr = f"({leftExpr} {op} {rightExpr})"
                subExpressions.append(newExpr)
                intermediateResults[newExpr] = result
            operators.append("->")
            i += 1
        elif char == "<" and i + 2 < len(expression) and expression[i + 1:i + 3] == "=>":
            # Handle biconditional operator
            while (operators and operators[-1] != "(" and
                   precedence[operators[-1]] >= precedence["<=>"]):
                op = operators.pop()
                right = stack.pop()
                rightExpr = subExpressions.pop()
                left = stack.pop()
                leftExpr = subExpressions.pop()
                result = applyOperator(op, left, right)
                stack.append(result)
                newExpr = f"({leftExpr} {op} {rightExpr})"
                subExpressions.append(newExpr)
                intermediateResults[newExpr] = result
            operators.append("<=>")
            i += 2
        elif char == "(":
            operators.append(char)  # Push '(' onto the operator stack
        elif char == ")":
            # Evaluate until the matching '(' is found
            while operators and operators[-1] != "(":
                op = operators.pop()  # Get the operator
                right = stack.pop()  # Get the right operand
                rightExpr = subExpressions.pop()  # Corresponding expression
                left = stack.pop()  # Get the left operand
                leftExpr = subExpressions.pop()  # Corresponding expression
                result = applyOperator(op, left, right)  # Apply the operator
                stack.append(result)  # Push result back onto the stack
                newExpr = f"({leftExpr} {op} {rightExpr})"  # Form the new expression
                subExpressions.append(newExpr)
                intermediateResults[newExpr] = result  # Store the result

            operators.pop()  # Remove the '(' from the stack
        i += 1  # Move to the next character

    # Evaluate any remaining operators
    while operators:
        op = operators.pop()  # Get the next operator
        right = stack.pop()  # Right operand
        rightExpr = subExpressions.pop()  # Corresponding expression
        left = stack.pop()  # Left operand
        leftExpr = subExpressions.pop()  # Corresponding expression
        result = applyOperator(op, left, right)  # Apply the operator
        stack.append(result)  # Push the final result onto the stack
        newExpr = f"({leftExpr} {op} {rightExpr})"  # Form the final expression
        subExpressions.append(newExpr)
        intermediateResults[newExpr] = result  # Store the final result

    return stack[0], intermediateResults  # Return final result and intermediate results

def validateInput(userInput):
    """Check if the input expression contains only valid characters and has at least one operator."""
    validChars = set("pqr()~^v-><=>")  # Set of valid characters
    userInput = userInput.replace(" ", "")  # Remove spaces for validation

    if not all(char in validChars for char in userInput):
        raise ValueError("Invalid input. Only the following characters are allowed: p,q,r,~,^,v,->,<=>,(,)")

    # Check for balanced parentheses
    if userInput.count('(') != userInput.count(')'):
        raise ValueError("Invalid statement. Unmatched parentheses.")

    # Check for invalid patterns (e.g., two operators in a row)
    previousChar = ''
    i = 0
    while i < len(userInput):
        char = userInput[i]
        
        # Check for multi-character operators
        if i + 1 < len(userInput) and userInput[i:i+2] == "->":
            if previousChar in "^v-><=>~":
                raise ValueError("Invalid statement. Use of operators is invalid.")
            previous_char = "->"
            i += 2
            continue
        elif i + 2 < len(userInput) and userInput[i:i+3] == "<=>":
            if previousChar in "^v-><=>~":
                raise ValueError("Invalid statement. Use of operators is invalid.")
            previousChar = "<=>"
            i += 3
            continue

        if char == "~" and i + 1 < len(userInput) and userInput[i + 1] == "(":
            previousChar = char
            i += 1
            continue
        
        # Check for consecutive single-character operators
        if char in "^v":
            if previousChar in "^v-><=>~":
                raise ValueError("Invalid statement. Use of operators is invalid.")
    
        previousChar = char
        i += 1

    # Check if the expression starts or ends with an operator
    if userInput[0] in "^v-><=>" or userInput[-1] in "^v-><=>":
        raise ValueError("Invalid statement. Expression cannot start or end with an operator.")

    # Check for presence of at least one operator, allowing unary expressions
    if not any(op in userInput for op in "^v-><=>") and not (userInput.startswith("~") and len(userInput) > 1):
        raise ValueError("Invalid statement. At least one logical operator is required.")

# Main loop for user input remains unchanged


# Main loop for user input
while True:
    choice = input("[1] Input an expression\n[2] Load the expression from input.txt\nChoice: ")

    while choice not in ["1", "2"]:
        choice = input("Invalid choice. Please enter 1 or 2\nChoice: ")

    if choice == "1":
        userInput = input("Enter Logical Statement: ").lower().replace(" ", "")
    elif choice == "2":
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        filePath = filedialog.askopenfilename(title="Select file", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if filePath:
            with open(filePath, 'r') as file:
                userInput = file.read().strip().lower().replace(" ", "")
        else:
            print("No file selected. Exiting.")
            break

    try:
        validateInput(userInput)  # Validate the input expression
    except ValueError as e:
        print(e)
        while True:
            continueDecision = input("Do you want to try again? (y/n): ").lower()
            if continueDecision in ['y', 'n']:
                break
            else:
                print("Invalid choice. Try again.")
        
        if continueDecision != 'y':
            print("Thank you for using our program!")
            break
        else:
            continue

    # Get truth values for p, q, r based on user input
    p, q, r = getValues(userInput)

    headers = []  # To hold headers for the output table
    data = []  # To hold data for the output table

    # Determine which headers to display based on the input
    if "p" in userInput and "q" in userInput and "r" in userInput:
        headers = ["p", "q", "r"]
        data = [[p[x], q[x], r[x]] for x in range(8)]
    elif "p" in userInput and "q" in userInput:
        headers = ["p", "q"]
        data = [[p[x], q[x]] for x in range(4)]
    elif "p" in userInput and "r" in userInput:
        headers = ["p", "r"]
        data = [[p[x], r[x]] for x in range(4)]
    elif "q" in userInput and "r" in userInput:
        headers = ["q", "r"]
        data = [[q[x], r[x]] for x in range(4)]
    elif "p" in userInput:
        headers = ["p"]
        data = [[p[x]] for x in range(2)]
    elif "q" in userInput:
        headers = ["q"]
        data = [[q[x]] for x in range(2)]
    elif "r" in userInput:
        headers = ["r"]
        data = [[r[x]] for x in range(2)]

    # Evaluate the logical expression and get intermediate results
    result, intermediateResults = evalExpression(userInput, p, q, r)

    # Insert intermediate results before the final result in the data
    for expr in intermediateResults.keys():
        headers.append(expr)  # Add intermediate expression to headers
        for i in range(len(data)):
            data[i].append(intermediateResults[expr][i])  # Append intermediate results to each row

    # Prepare final result for output
    headers.append(f"Final Answer for: {userInput}")
    if "p" in userInput and "q" in userInput and "r" in userInput:
        for x in range(8):
            data[x].append(result[x])
    elif ("p" in userInput and "q" in userInput) or ("p" in userInput and "r" in userInput) or ("q" in userInput and "r" in userInput):
        for x in range(4):
            data[x].append(result[x])
    else:
        for x in range(2):
            data[x].append(result[x])

    # Print the results in a formatted table
    print(tabulate(data, headers, numalign="center", tablefmt="heavy_outline"))

    while True:
        continueChoice = input("Do you want to continue? (y/n): ").lower()
        if continueChoice == 'y':
            break
        elif continueChoice == 'n':
            print("Thank you for using our program!")
            exit()
        else:
            print("Invalid choice. Try again.")