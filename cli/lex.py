def lex(input: str):
    filters = {}
    currentStr = ""
    currentKey = ""
    eqReading = False
    for char in input:
        if char.isalnum() or char == '.' or char == '_' or char == '/':
            currentStr += char
        elif char == '(' or char == ')' or char == '"' or char == "'":
            continue
        elif char == ' ':
            if currentStr == 'or' or currentStr == 'and' or currentStr == 'filter':
                currentStr = ""
                continue
            if eqReading:
                # space before val
                if currentStr == "":
                    continue
                else:
                    filters[currentKey].append(currentStr)
                    currentStr = ""
                    currentKey = ""
                    eqReading = False
            else:
                # space after key before =
                continue
        elif char == '=':
            eqReading = True
            currentKey = currentStr
            if currentKey not in filters:
                filters[currentKey] = []
            currentStr = ""
            continue
    filters[currentKey].append(currentStr)
    return filters
