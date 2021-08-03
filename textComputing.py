##############################
# UTILITY FUNCTIONS FOR TEXT #
#         01/08/21           #
##############################


import unicodedata


#############
# FUNCTIONS #
#############


def normalize(text):
    text = unicodedata.normalize("NFD", text)\
           .encode("ascii", "ignore")\
           .decode("utf-8")

    return str(text).lower()
