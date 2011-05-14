"""
"""

class EditDistance():
    """
    """
    def __init__(self, Table, kwattr):
        """
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
        return set(w for w in word if w in self.wordlist)
    
    def edit(self, word):
        splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes    = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
        inserts    = [a + c + b     for a, b in splits for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)
    
    def edit1(self, word):
        pass
    
    def correct(self, word):
        results = self.match(self.edit(word))
        print "result for " + word + " is: "
        print results
        #return max(results, key=self.wordlist.get)
        