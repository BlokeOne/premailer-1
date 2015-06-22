# Test Error Classes - Makes error message readable


class PremailerError(Exception):
    def __init__(self, message):
        self.message = message
        Exception.__init__(self, message)


class XMLSyntaxError(PremailerError):
    def __init__(self, message):
        super(PremailerError, self).__init__(message)


class CSS_SyntaxError(PremailerError):
    def __init__(self, message):
        super(PremailerError, self).__init__(message)

        # ERROR: "background-color: lighblue;"
        # Should be: "ERROR Property: Invalid value for property: background-color: lighblue  - Line: 8, Column: 17"
        if message.startswith("ERROR Property: Invalid"):
            message, info = message.rsplit(']', 1)[0].rsplit('[', 1)
            msg1, junk, msg2 = message.split('"', 2)
            msg2, msg3 = msg2.split(':', 1)
            line, column, propertyvalue = info.split(":", 2)
            message = "{0}{1}: \"{2}: {3}\" - Line: {4} Column: {5}".format(msg1, msg2.strip(), propertyvalue.strip(),
                                                                            msg3.strip(), line, column)

        # ERROR: "background #fffef0;"
        # Should be: "ERROR Property: No ":" after name found: background-color lightblue - Line: 8, Column: 34"
        elif message.startswith("ERROR Property: No \":\""):
            message, info = message.split('found:', 1)
            propertyvalue, restofmsg = info.split('[', 1)
            line, column, left = restofmsg.split(':', 2)
            message = "{0}found: \"{1}\" - Line {2} Column: {3}".format(message, propertyvalue.strip(), line, column)

        # ERROR: "background: light!blue;"
        # Should be: "ERROR Property: No CSS priority value - Line: 10, Column: 17"
        elif message.startswith("ERROR Property: No CSS priority value: "):
            message, info, restofmsg = message.split(':', 2)
            restofmsg, column, left = restofmsg.rsplit(':', 2)
            left, line = restofmsg.rsplit('[', 1)
            message = "{0}:{1} - Line: {2}, Column: {3}".format(message, info, line, column)

        # ERROR: "background: #ffef0;" TODO explore other options
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
                try:
                    # print message
                    left, propertytype, value = message.rsplit(':', 2)
                    propertyvalue = propertytype + ": " + value.strip()
                    left, errorlocation = left.rsplit(':', 1)
                    errortype, restofmsg = message.split(':', 1)
                    left, restofmsg = restofmsg.split('\'CHAR\'', 1)
                    left, restofmsg = restofmsg.split('\'', 1)
                    left, restofmsg = restofmsg.split(',', 1)
                    line, restofmsg = restofmsg.split(',', 1)
                    column, restofmsg = restofmsg.split(')', 1)
                    message = "{0} :{1} : \"{2}\" - Line:{3}, Column:{4}".format(errortype, errorlocation,
                                                                                 propertyvalue.strip(), line, column)
                except:
                    try:
                        left, message = message.rsplit('-', 1)
                        message = "We have found an error above:{0}".format(message)
                    except:
                        print "Error - Test"



        # ERROR: Gibberish-Before
        # @media screen {
        # Should be: ERROR SelectorList: "@media" Invalid Selector - Line: 5, Column: 9
        elif message.startswith("ERROR Unexpected token"):
            message, info = message.split(')', 1)
            left, restofmsg = message.split(',', 1)
            errorrule, line, column = restofmsg.split(',', 2)
            errortype, propertyvalue, restofmsg = info.split(':', 2)
            message = "{0}: \"{1}\" {2} - Line:{3}, Column:{4}".format(errortype.strip(), errorrule.strip(),
                                                                       propertyvalue.strip(), line, column)

        # ERROR: [@media screen {
        # Should be: ERROR Selector: "@media" Unexpected CHAR. [4 - Line: 4, Column: 10
        elif "ERROR Unexpected token" in message:
            message, info = message.split(')', 1)
            left, restofmsg = message.split(',', 1)
            errorrule, line, column = restofmsg.split(',', 2)
            errortype, propertyvalue, restofmsg = info.split(':', 2)
            print propertyvalue
            message = "{0}: \"{1}\" {2} - Line:{3}, Column:{4}".format(errortype.strip(), errorrule.strip(),
                                                                       propertyvalue.strip(), line, column)

        # **************************************************************************#
        # *************************** WARNING Messages *****************************#
        # **************************************************************************#
        # WARNING "backgrund: #fffef0;"
        # Should do: "WARNING Property: Unknown Property name: "backgrund" - Line: 4, Column: 17"
        elif message.startswith("WARNING Property:") or \
                message.startswith("WARNING CSSStylesheet: Unknown @rule found."):
            message, info = message.rsplit(']', 1)[0].rsplit('[', 1)
            message, junk = message.rsplit('.', 1)
            line, column, propertyvalue = info.split(":", 2)
            message = "{0}: \"{1}\" - Line: {2}, Column: {3}".format(message, propertyvalue.strip(), line, column)

        Exception.__init__(self, message)


class HTMLElementError(PremailerError):  # TODO delete and remove try/except from code
    def __init__(self, message):
        super(PremailerError, self).__init__(message)
        # ERROR: "<head>>"
        # Should be: "Unexpected end tag: "head" - Line: 73, Column: 16 - Check Opening " head" tag."
        if str(message).startswith("Unexpected end tag"):
            msg, left = str(message).split(':', 1)
            element, restofmsg = left.split(',', 1)
            junk, restofmsg = restofmsg.strip().split(' ', 1)
            line, restofmsg = restofmsg.split(',', 1)
            junk, column = restofmsg.strip().split(' ', 1)
            message = msg.strip() + ": \"" + element.strip() + "\" - Line: " + line + ", Column: " + column + \
                " - Check Opening \"" + element + "\" tag."
        Exception.__init__(self, message)