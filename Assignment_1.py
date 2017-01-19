##       Assignment_1 - INF 141 Information Visualization
##
##             By: Raymond Tang 87082176 01/18/2017
#
#

import string
from collections import Counter

class TextProcesser(object):
# -------------------------------------------------------------
#                 Part A: Word Frequenceies
# -------------------------------------------------------------
    def __init__(self, szFile):
        def tokenize(self):
            file = open(self.File).read()      #store file as a string
            Tokenized = []
            for word in file.split():       #For each word in file split on spaces
                Tokenized.append("".join(letter for letter in word if letter not in string.punctuation))        #Add string to list strip punctuation
            return Tokenized

        self.File = szFile
        self.ListOfWords = tokenize(self)

    def computeWordFrequencies(self):
        return Counter(self.ListOfWords)       #return counter of words in list

    def mostFrequent(self):
        return self.computeWordFrequencies().most_common()

# -------------------------------------------------------------
#              Part B: Intersection of Two Files
# -------------------------------------------------------------
    def compare(self, TextObject):
        return set(self.ListOfWords) & set(TextObject.ListOfWords)




def main():
    file = raw_input("Enter name of file to process: ")
    TextObject = TextProcesser(file)
    print ("-------------------------------------------------------------")
    print ("")
    print ("The most frequent words are: ")
    for word, count in TextObject.mostFrequent():
        print ('%27s: %d' % (word, count))
    print ("")
    print ("")
    compare_mode = raw_input("Would you like to compare this file to another? Y/N")
    if compare_mode == "Y":
        file2 = raw_input("Enter name of file to copmare: ")
        print ("-------------------------------------------------------------")
        TextObject2 = TextProcesser(file2)
        compared = TextObject.compare(TextObject2)
        print ("")
        print ("There are, %s, matches" % len(compared))
        counter = 0

        print (", ".join(compared))

if __name__ == "__main__":
    main()