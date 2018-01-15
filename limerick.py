#!/usr/bin/env python
import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit

# Use word_tokenize to split raw text into words
from string import punctuation

import nltk
from nltk.tokenize import word_tokenize

scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')

def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)



class LimerickDetector:

    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()


    def num_syllables(self, word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.
        """
        # TODO: provide an implementation!
        if word not in self._pronunciations:
          return 1
        
        list_len=0
        ftime_syllable_count=0
        min_syllable_count=0
        for pronounce in self._pronunciations[word]:
          list_len=len(self._pronunciations[word])
          count_syllable=0
        
          for item in pronounce:
               if '0' in item or '1' in item or '2' in item:
                    count_syllable+=1 
          if(ftime_syllable_count==0): #if it the first time
               min_syllable_count=count_syllable
          elif(count_syllable<min_syllable_count):
               min_syllable_count=count_syllable

        return min_syllable_count
        
    def rhymes(self, a, b):
        """
        Returns True if two words (represented as lower-case strings) rhyme,
        False otherwise.
        """

        # TODO: provide an implementation!

        if a not in self._pronunciations or b not in self._pronunciations :
          return False



        for pA in self._pronunciations[a]:
          strA=""
          strA=''.join(pA)
          #remove the consonants
          indexA=0
          while indexA<len(strA):
                if strA[indexA]!='A' and strA[indexA]!='E' and strA[indexA]!='I' and strA[indexA]!='O' and strA[indexA]!='U':
                     indexA+=1
                else:
                     break

          strA= strA[indexA:]
          lenA=len(strA)
          for pB in self._pronunciations[b]:
              
              strB=""
              #convert each list to string
              
              strB=''.join(pB)
          
              indexB=0
              while indexB<len(strB):
                    if strB[indexB]!='A' and strB[indexB]!='E' and strB[indexB]!='I' and strB[indexB]!='O' and strB[indexB]!='!':
                         indexB+=1
                    else:
                         break
              strB= strB[indexB:] 

              
              lenB=len(strB)

              #check if the length of pronunciations are equal and if both are equal
              if lenA==lenB:
                if strA==strB:
                  return True
              #if the lengths are different; check if one is suffix of another
              if lenA>lenB:
               if strA.endswith(strB):
                    return True
      
              if lenB>lenA:
               if strB.endswith(strA):
                    return True

        return False

    def is_limerick(self, text):
        """
        Takes text where lines are separated by newline characters.  Returns
        True if the text is a limerick, False otherwise.

        A limerick is defined as a poem with the form AABBA, where the A lines
        rhyme with each other, the B lines rhyme with each other, and the A lines do not
        rhyme with the B lines.


        Additionally, the following syllable constraints should be observed:
          * No two A lines should differ in their number of syllables by more than two.
          * The B lines should differ in their number of syllables by no more than two.
          * Each of the B lines should have fewer syllables than each of the A lines.
          * No line should have fewer than 4 syllables

        (English professors may disagree with this definition, but that's what
        we're using here.)


        """
        # TODO: provide an implementation!
        strlist=text.strip().split('\n')


        newlist=[]
        strpunct=['',',','?','!',':',';','-','.','``']
        for listitem in strlist:
          listitem=word_tokenize(listitem)
          # listitem=self.apostrophe_tokenize(listitem)
          newlistitem=list(filter(lambda a: a not in strpunct, listitem))
          newlist.append(newlistitem)

        if len(newlist)!=5:
          return False
        
        #count the no of syllables of each line
        ##############LIST1#########################
        count1=0

        list1=newlist[0]

        for word in list1:
          count1+=self.num_syllables(word)  
    
        # ##############LIST2#########################
        count2=0

        list2=newlist[1]

        for word in list2:
          count2+=self.num_syllables(word)  
 
        # ##############LIST3#########################
        count3=0

        list3=newlist[2]

        for word in list3:
          count3+=self.num_syllables(word)    
        
        # ##############LIST4#########################
        count4=0

        list4=newlist[3]

        for word in list4:
          count4+=self.num_syllables(word)    
        
        # ##############LIST5#########################
        count5=0

        list5=newlist[4]

        for word in list5:
          count5+=self.num_syllables(word)  

        #############Syllable constraints################
       

        if count1<4 or count2<4 or count3<4 or count4<4 or count5<4:
          return False
        if abs(count1-count2)>2 or abs(count2-count5)>2 or abs(count1-count5)>2:
          return False  
        if abs(count3-count4)>2:
          return False
        if count3>count1 or count3>count2 or count3>count5:
          return False
        if count4>count1 or count4>count2 or count4>count5:
          return  False

         #############Rhyme constraints################
        if (self.rhymes(list1[-1],list2[-1])) and (self.rhymes(list2[-1],list5[-1])) and (self.rhymes(list1[-1],list5[-1])) and (self.rhymes(list3[-1],list4[-1])) and not(self.rhymes(list1[-1],list3[-1])):
          if not(self.rhymes(list2[-1],list3[-1])) and not(self.rhymes(list5[-1],list3[-1])) and not(self.rhymes(list1[-1],list4[-1])):
            if not(self.rhymes(list2[-1],list4[-1])) and not(self.rhymes(list5[-1],list4[-1])):
              return True

        return False


    def apostrophe_tokenize(self,liststr):    
        strlist=[]
        liststr=liststr.translate(None,punctuation)
        strlist=liststr.split(' ')
        return strlist

    def guess_syllable(self,word):
        
        print "GUESS SYLLABLES"
        word=word.lower()
        count_vowels=0
        
        #converting string to character array
        chArray=list(word)
        #print chArray

        for ch in word:
          if ch=='a' or ch=='e'or ch=='i'or ch=='o'or ch=='u':
            print ch
            count_vowels+=1

        #print "temp_count",count_vowels
        # if(word.endswith('a')or word.endswith('e') or word.endswith('i') or word.endswith('o') or word.endswith('u')):
        #   count_vowels-=1

        if(word.endswith('e')):
          count_vowels-=1

        if(word.endswith('le')):
          count_vowels+=1


        if word.endswith('y'):
          count_vowels+=1
        #print "temp_count1",count_vowels
        for i in range(1,len(chArray)-1):
            #print "i",i
            #print "chArray[i]",chArray[i]
            if (chArray[i]=='a' or chArray[i]=='e'or chArray[i]=='i' or chArray[i]=='o' or chArray[i]=='u') and chArray[i]==chArray[i-1]:
              count_vowels-=1
            if (chArray[i]=='a' or chArray[i]=='e'or chArray[i]=='i' or chArray[i]=='o' or chArray[i]=='u'):
              if (chArray[i-1]=='a' or chArray[i-1]=='e'or chArray[i-1]=='i' or chArray[i-1]=='o' or chArray[i-1]=='u') and chArray[i]!=chArray[i-1]:
                count_vowels-=1 
        print "count_vowels",count_vowels  

# The code below should not need to be modified
def main():
  parser = argparse.ArgumentParser(description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")




  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')

  ld = LimerickDetector()
  lines = ''.join(infile.readlines())
  outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))

if __name__ == '__main__':
  main()