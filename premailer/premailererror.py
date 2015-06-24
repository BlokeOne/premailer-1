# Test Error Classes - Makes error message readable

#   Error: This
#   Should be: This

#   Try: Formatted neat readable message,
#   Except: Default error message.


class PremailerError(Exception):
    def __init__(self, message):
        self.message = message
        Exception.__init__(self, message)

class CSS_SyntaxError(PremailerError):
    def __init__(self, message):
        super(PremailerError, self).__init__(message)

        # ERROR: "background-color: lighblue;"
        # Should be: "ERROR Property: Invalid value for property: background-color: lighblue  - Line: 8, Column: 17"
        if message.startswith("ERROR Property: Invalid"):
            try:
                message, info = message.rsplit(']', 1)[0].rsplit('[', 1)
                msg1, junk, msg2 = message.split('"', 2)
                msg2, msg3 = msg2.split(':', 1)
                line, column, propertyvalue = info.split(":", 2)
                message = "{0}{1}: \"{2}: {3}\" - Line: {4} Column: {5}".format(msg1, msg2.strip(), propertyvalue.strip(),
                                                                                msg3.strip(), line, column)
            except:
                Exception.__init__(self, message)

        # ERROR: "background: light!blue;"
        # Should be: "ERROR Property: No CSS priority value - Line: 10, Column: 17"
        elif message.startswith("ERROR Property: No CSS priority value: "):
            try:
                message, info, restofmsg = message.split(':', 2)
                restofmsg, column, left = restofmsg.rsplit(':', 2)
                left, line = restofmsg.rsplit('[', 1)
                message = "{0}:{1} - Line: {2}, Column: {3}".format(message, info, line, column)
            except:
                Exception.__init__(self, message)

        # ERROR: "background #fffef0;"
        # Should be: "ERROR Property: No ":" after name found: "background #ffffe0" - Line 4 Column: 28"
        elif message.startswith("ERROR Property: No"):
            try:
                message, info = message.split('found:', 1)
                propertyvalue, restofmsg = info.split('[', 1)
                line, column, left = restofmsg.split(':', 2)
                message = "{0}found: \"{1}\" - Line {2} Column: {3}".format(message, propertyvalue.strip(), line, column)
            except:
                Exception.__init__(self, message)

        # ERROR: "background: ;"
        # ERROR: "background: }#fffef0;"
        # Should be: "ERROR CSSStyleDeclaration: Syntax Error in Property: background: "
        elif message.startswith("ERROR No content"):
            try:
                message = message.split(':', 2)[2].strip()
                message = message.split('ERROR CSSStyleRule:', 1)[0]
            except:
                Exception.__init__(self, message)

        # ERROR: "background: #ffef0;"
        # Should be: "ERROR PropertyValue: Syntax Error in Property: background: #ffef0 - Line: 4, Column: 29"
        elif message.startswith("ERROR PropertyValue:"):
            try:
                left, propertytype, value = message.rsplit(':', 2)
                propertyvalue = propertytype + ": " + value.strip()
                left, errorlocation = left.rsplit(':', 1)
                errortype, restofmsg = message.split(':', 1)
                left, restofmsg = restofmsg.split('\'HASH\'', 1)
                left, restofmsg = restofmsg.split('\'', 1)
                left, restofmsg = restofmsg.split(',', 1)
                line, restofmsg = restofmsg.split(',', 1)
                column, restofmsg = restofmsg.split(')', 1)
                message = "{0} :{1} : \"{2}\" - Line:{3}, Column:{4}".format(errortype, errorlocation,
                                                                             propertyvalue.strip(), line, column)
                
        # ERROR: "background: ##fffef0;"
        # Should be: "ERROR PropertyValue : Syntax Error in Property : "background: ##fffef0" - Line: 4, Column: 29"
            except:
                # ERROR: "background:{ #fffef0;"
                # Should be: "Found: '{' - Line: 5, Column: 28"
                if "ERROR CSSMediaRule:" in message:
                    try:
                        msg = message.split("'CHAR', u", 1)[1]
                        junk, problem, msg = msg.split("'", 2)
                        junk, line, msg = msg.split(",", 2)
                        column, msg = msg.split(")", 1)
                        message = "Found: '{0}' - Line:{1}, Column:{2}".format(problem, line, column)
                    except:
                        Exception.__init__(self, message)
                else:
                    try:
                        left, propertytype, value = message.rsplit(':', 2)
                        propertyvalue = propertytype + ": " + value.strip()
                        left, errorlocation = left.rsplit(':', 1)
                        errortype, restofmsg = message.split(':', 1)
                        left, restofmsg = restofmsg.split('\'CHAR\'', 1)
                        left, restofmsg = restofmsg.split('\'', 1)
                        left, restofmsg = restofmsg.split(',', 1)
                        line, restofmsg = restofmsg.split(',', 1)
                        column, restofmsg = restofmsg.split(')', 1)
                        message = "{0}:{1}: \"{2}\" - Line:{3}, Column:{4}".format(errortype, errorlocation,
                                                                                   propertyvalue.strip(), line, column)
                    except:
                        left, message = message.rsplit('-', 1)
                        message = "We have found an error above:{0}".format(message)

        # ** @ Media Specific Errors ** #

        # ERROR: "Gibberish-Before @media screen {"
        # Should be: "ERROR SelectorList: "@media" Invalid Selector - Line: 5, Column: 9"
        elif message.startswith("ERROR Unexpected token"):
            try:
                message, info = message.split(')', 1)
                left, restofmsg = message.split(',', 1)
                errorrule, line, column = restofmsg.split(',', 2)
                errortype, propertyvalue, restofmsg = info.split(':', 2)
                message = "{0}: \"{1}\" {2} - Line:{3}, Column:{4}".format(errortype.strip(), errorrule.strip(),
                                                                           propertyvalue.strip(), line, column)
            except:
                try:
                    # ERROR: "@font-face a{"
                    # Should be: "ERROR Unexpected token : Found: a - Line: 14, Column: 20"
                    if message.startswith("ERROR Unexpected token (IDENT"):
                        errortype = message.split('(', 1)[0]
                        restofmsg, line, column = message.rsplit(',', 2)
                        identifiererrror = restofmsg.split(', ', 1)[1]
                        message = "{0}: Found: \"{1}\" - Line:{2}, Column:{3}".format(errortype, identifiererrror, line, column)
                except:
                    Exception.__init__(self, message)

        # ERROR: "[@media screen {"
        # Should be: "ERROR Selector: "@media" Unexpected CHAR. [4 - Line: 4, Column: 10"
        elif "ERROR Unexpected token" in message:
            try:
                message, info = message.split(')', 1)
                left, restofmsg = message.split(',', 1)
                errorrule, line, column = restofmsg.split(',', 2)
                errortype, propertyvalue, restofmsg = info.split(':', 2)
                message = "{0}: \"{1}\" {2} - Line:{3}, Column:{4}".format(errortype.strip(), errorrule.strip(),
                                                                           propertyvalue.strip(), line, column)
            except:
                Exception.__init__(self, message)

        # ERROR: "@media screnen {"
        # Should be: "ERROR MediaQuery: Found: 'screnen' - Line: 2, Column: 16"
        elif "ERROR MediaQuery" in message:
            try:
                errortype, message = message.split(':', 1)
                message = message.rsplit('ERROR MediaQuery: No match', 1)[0]
                restofmsg, line, column = message.rsplit(',', 2)
                column = column.split(')', 1)[0]
                identifiererrror = restofmsg.split(', u', 1)[1]
                message = "{0}: Found: {1} - Line:{2}, Column:{3}".format(errortype, identifiererrror, line, column)

            except:
                Exception.__init__(self, message)

        # ERROR: "@media screen a {"
        # Should be: "ERROR MediaList: Found: 'a' - Line: 3, Column: 23"
        elif "ERROR MediaList" in message:
            try:
                errortype = message.split(':', 1)[0]
                restofmsg, line, column = message.rsplit(',', 2)
                column = column.split(')', 1)[0]
                identifiererrror = restofmsg.split(', u', 1)[1]
                message = "{0}: Found: {1} - Line:{2}, Column:{3}".format(errortype, identifiererrror, line, column)

            except:
                Exception.__init__(self, message)


        # *************************** WARNING Messages ***************************** #

        # WARNING "backgrund: #fffef0;"
        # Should do: "WARNING Property: Unknown Property name: "backgrund" - Line: 4, Column: 17"
        elif message.startswith("WARNING Property:") or \
                message.startswith("WARNING CSSStylesheet: Unknown @rule found."):
            try:
                message, info = message.rsplit(']', 1)[0].rsplit('[', 1)
                message, junk = message.rsplit('.', 1)
                line, column, propertyvalue = info.split(":", 2)
                message = "{0}: \"{1}\" - Line: {2}, Column: {3}".format(message, propertyvalue.strip(), line, column)
            except:
                Exception.__init__(self, message)

        Exception.__init__(self, message)


class HTMLElementError(PremailerError):
    def __init__(self, message):
        super(PremailerError, self).__init__(message)
        # ERROR: "<head>>"
        # Should be: "Unexpected end tag: "head" - Line: 73, Column: 16 - Check Opening " head" tag."
        if str(message).startswith("Unexpected end tag"):
            try:
                msg, left = str(message).split(':', 1)
                element, restofmsg = left.split(',', 1)
                junk, restofmsg = restofmsg.strip().split(' ', 1)
                line, restofmsg = restofmsg.split(',', 1)
                junk, column = restofmsg.strip().split(' ', 1)
                message = msg.strip() + ": \"" + element.strip() + "\" - Line: " + line + ", Column: " + column + \
                    " - Check Opening \"" + element + "\" tag."
            except:
                Exception.__init__(self, message)

        Exception.__init__(self, message)