"""
This File Stores The Edit Distance Class used in views.py
for the text queries 
"""

class EditDistance():
    """
    Edit Distance Class that performs the Edit Distance algorithm successively on a word
    until a resultset is found or the len of the word is longer that the count of edit distances.
    Words with the ORM, and the table and keyword attribute need to be passed in
    """
    def __init__(self, Table, kwattr):
        """
        Table is the table in the model that stores the keywords
        and kwattr is the keyword attribute to access that keyword
        Populates the Keyword list from the database and sets the alphabet to be a-z
        assuming the database stores everything in lower case
        """
        keywords = Table.objects.only(kwattr).distinct()
        self.wordlist = []
        self.alphabet = ''
        for letter in xrange(ord('a'), ord('z')+1):
            self.alphabet += chr(letter)
        for keywordobj in keywords:
            word = getattr(keywordobj, kwattr)
            self.wordlist.append(word)
        
    def match(self, word):
        """
        Returns all the keywords that match 
        """
        return set(w for w in word if w in self.wordlist)
    
    def edit(self, word):
        """
        performs a 1 character edit distance on the word and tries to match it
        to the word list
        Returns a set of the results
        """
        splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes    = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
        inserts    = [a + c + b     for a, b in splits for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)
    
    def editRec(self, curres):
        """
        Performs a recursive edit on the edit results, curres
        """
        return set(edits for curedit in curres for edits in self.edit(curedit) if edits in self.wordlist)
    
    def correct(self, word):
        """
        Performs successive edit distances on the word up to it's length and returns the result set
        and the number of edits required for that result set (the diff)
        """
        #word is exact match so we dont need an edit distance on it
        if word in self.wordlist:
            return []
        
        curedit = self.edit(word)
        editcnt = 1
        results = []
        while not results and editcnt < len(word):
            results = self.match(curedit)
            if not results:
                curedit = self.editRec(curedit)
                editcnt += 1
        
        print "result for " + word + " is: "
        print results
        print "after " + str(editcnt) + " edits!"
        return results, editcnt
        #return max(results, key=self.wordlist.get)
        