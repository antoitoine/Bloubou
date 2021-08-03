###################
# Utility Library #
#    01/08/21     #
###################


#############
# CONSTANTS #
#############


MESSAGES = ["[DEB]", "[CMD]", "[ERR]", "[MSG]", "[BOT]", "[MSC]"]
DEBUG_MESSAGE = 0
COMMAND_MESSAGE = 1
ERROR_MESSAGE = 2
USER_MESSAGE = 3
BOT_MESSAGE = 4
MYSC_MESSAGE = 5


#############
# FUNCTIONS #
#############


def printMessage(message, messageType, isText=False):
    """ Prints a message in the console """
    if not isText:
        print(MESSAGES[messageType], f"<{message.author}>", message.content)
    else:
        print(MESSAGES[messageType], message)
