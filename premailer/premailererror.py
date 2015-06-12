
# Test Error Classes
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
        if message.startswith("ERROR Property:"):
            msg, left = message.split('[', 1)
            line, column, left = left.split(':', 2)
            line = ", Line: " + line
            location = line + ", Column: " + column
            value = " (" + left.strip().rsplit(']', 1)[0] + ")"
            msg1, junk, msg2, = msg.split('"', 2)
            message = msg1 + msg2.strip() + value + location

        # ERROR: "background: #ffef0;"
        # Should be: "ERROR PropertyValue: background:#ffef0, Line: 4, Column: 29"
        elif message.startswith("ERROR PropertyValue:"):
            left, property, value = message.rsplit (':', 2)
            propertyvalue = property + ":" + value.strip()
            errortype, restofmsg = message.split(':', 1)
            left, restofmsg = restofmsg.split('\'HASH\'', 1)
            left, restofmsg = restofmsg.split('\'', 1)
            left, restofmsg = restofmsg.split(',', 1)
            line, restofmsg = restofmsg.split(',', 1)
            column, restofmsg = restofmsg.split(')', 1)
            printmsg = errortype + ":" + propertyvalue + ", Line:" + line + ", Column:" + column
            message = printmsg
        Exception.__init__(self, message)


class HTMLElementError(PremailerError):  #TODO : HTML only throwing "head" element error
    def __init__(self, message):
        super(PremailerError, self).__init__(message)
        print message
        if str(message).startswith("Unexpected end tag"):
            message = str(message) + " - Check start tag for error."
            msg, left = message.split(':', 1)
            element, restofmsg = left.split(',', 1)
            element = element.strip()
            junk, restofmsg2 = restofmsg.strip().split(' ', 1)
            line, restofmsg3 = restofmsg2.split(',', 1)
            junk, restofmsg4 = restofmsg3.strip().split(' ', 1)
            column, restofmsg5 = restofmsg4.strip().split(' ', 1)
            msg1 = "Element: \"" + element + "\" - Line: " + line + ", Column: " + column + " - Also check starting \"" + element + "\" tag."

            message = msg1
        Exception.__init__(self, message)

        if "ERROR Property:" in message:
            msg, left = message.split('[', 1)
            line, column, left = left.split(':', 2)
            line = ", Line: " + line
            location = line + ", Column: " + column
            value = " (" + left.strip().rsplit(']', 1)[0] + ")"
            msg1, junk, msg2, = msg.split('"', 2)
            message = msg1 + msg2.strip() + value + location
        Exception.__init__(self, message)