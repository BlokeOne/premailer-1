
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
        # ERROR: "background-color: lighblue;"
        # Should be: "ERROR Property: Invalid value for property: background-color: lighblue  - Line: 8, Column: 17"
        super(PremailerError, self).__init__(message)
        if message.startswith("ERROR Property: Invalid"):
            message, info = message.rsplit(']', 1)[0].rsplit('[', 1)
            msg1, junk, msg2 = message.split('"', 2)
            msg2, msg3 = msg2.split(':', 1)
            line, column, propertyvalue = info.split(":", 2)
            message = msg1 + msg2.strip() + ":" + propertyvalue + ":" + msg3.strip() + " - Line: " + line + ", Column: " \
                + column

        # ERROR: "background #fffef0;"
        # Should be: "ERROR Property: No ":" after name found: background-color lightblue - Line: 8, Column: 34"
        elif message.startswith("ERROR Property: No"):
            print message
            message, info = message.split('found:', 1)

            propertyvalue, restofmsg = info.split('[', 1)
            line, column, left = restofmsg.split(':', 2)
            message = message + "found: " + propertyvalue.strip() + " - Line: " + line + ", Column: " + column

        # ERROR: "background: #ffef0;"
        # Should be: "ERROR PropertyValue: Syntax Error in Property: background: #ffef0 - Line: 4, Column: 29"
        elif message.startswith("ERROR PropertyValue:"):
            # print message
            left, propertytype, value = message.rsplit(':', 2)
            propertyvalue = propertytype + ": " + value.strip()
            left, errorlocation = left.rsplit(':', 1)
            errortype, restofmsg = message.split(':', 1)
            left, restofmsg = restofmsg.split('\'HASH\'', 1)
            left, restofmsg = restofmsg.split('\'', 1)
            left, restofmsg = restofmsg.split(',', 1)
            line, restofmsg = restofmsg.split(',', 1)
            column, restofmsg = restofmsg.split(')', 1)
            message = errortype + ":" + errorlocation + ":" + propertyvalue + " - Line:" + line + ", Column:" + column

        # Test case
        elif message.startswith("ERROR COLOR_VALUE:"):
            message, left = message.split(":", 1)
            info = left.split("'HASH', ", 1)[1]
            info = info.split("'", 1)[1]
            value, numbersandstuff = info.rsplit("'", 1)
            numbers = numbersandstuff.split(")", 1)[0].replace(",", "").strip()
            value = ": (" + value + ") "
            line, column = numbers.split(" ", 1)
            line = "Line " + line + ", "
            column = "Column " + column
            message = message + value + line + column

        # WARNING Messages
        # WARNING "backgrund: #fffef0;"
        # Should do: "WARNING Property: Unknown Property name: "backgrund" - Line: 4, Column: 17"
        elif message.startswith("WARNING Property:"):
            message, info = message.rsplit(']', 1)[0].rsplit('[', 1)
            message, junk = message.rsplit('.', 1)
            line, column, propertyvalue = info.split(":", 2)
            message = message + ":" + " \"" + propertyvalue.strip() + "\"" + " - Line: " + line + ", Column: " + column

        Exception.__init__(self, message)


class HTMLElementError(PremailerError):  # TODO delete and remove try/except from code
    def __init__(self, message):
        super(PremailerError, self).__init__(message)
        # ERROR: "<head>>"
        # Should be: "Unexpected end tag: "head" - Line: 73, Column: 16 - Check Opening " head" tag."
        # if str(message).startswith("Unexpected end tag"):
        #     msg, left = str(message).split(':', 1)
        #     element, restofmsg = left.split(',', 1)
        #     junk, restofmsg = restofmsg.strip().split(' ', 1)
        #     line, restofmsg = restofmsg.split(',', 1)
        #     junk, column = restofmsg.strip().split(' ', 1)
        #     message = msg.strip() + ": \"" + element.strip() + "\" - Line: " + line + ", Column: " + column + \
        #         " - Check Opening \"" + element + "\" tag."

        # if "ERROR Property:" in message:
        #     msg, left = message.split('[', 1)
        #     line, column, left = left.split(':', 2)
        #     line = ", Line: " + line
        #     location = line + ", Column: " + column
        #     value = " (" + left.strip().rsplit(']', 1)[0] + ")"
        #     msg1, junk, msg2, = msg.split('"', 2)
        #     message = msg1 + msg2.strip() + value + location
        # Exception.__init__(self, message)