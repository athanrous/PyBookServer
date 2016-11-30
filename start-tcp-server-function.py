#!/usr/bin/env python
# -*- coding: utf-8 -*-
import SocketServer
import socket
import tarfile
import os
import re
import sys
import itertools
from collections import Counter
from collections import defaultdict

class EchoRequestHandler(SocketServer.StreamRequestHandler): 
       
    def create_dictionary_words(self):
        
        "This function processes the data from the text files"
        "The output of this function is a dictionary which contains the path of each file we process and the content of the file"
        
        #Uncompress the tar.gz file and change the current path to the extracted folder.
        cur_path = os.getcwd()
        tar_path = cur_path + '/books_tmp.tar.gz'
        fin_path = cur_path + '/books_tmp/'
        
        #Check if extracted folder exists already
        if os.path.exists(fin_path):    
            dirs = os.listdir(fin_path)
        else:
            tar = tarfile.open(tar_path)
            tar.extractall()
            dirs = os.listdir(fin_path)
        
        #Create 2 lists and 1 dictionary. In the dictionary will be stored all the data 
        #with the following format {'file_name':'file_content'}         
        #no_pure = [] #List where all the lines of each file will be stored [before the removal of punctuation and numbers]
        #pure = [] # List where we append all the lines of we process [after the removal of punctuation and numbers]

        self.files_dict = {}

        for i in range(len(dirs)):
            
            no_pure = []
            cur_file = open(fin_path+dirs[i],'r')
             
            for line in cur_file.readlines():
                
                a = line.strip().split() #Split each line of the file
                no_pure.append(a)
                self.files_dict[dirs[i]] = no_pure
                cur_file.close()
            
        for k,v in self.files_dict.iteritems():
            pure = []
            for i in range(len(v)):
                if len(v[i]) > 0 :           
                    for j in range(len(v[i])):
                        
                        #Use of regular expressions to process the text                        
                        a_text = re.sub(r'^https?:\/\/.*[\r\n]*', '', v[i][j], flags=re.MULTILINE)
                        b_text = re.sub(r'[?|$|.|!|-]',r'',a_text)
                        c_text = re.sub(r'[^a-zA-ZäüöÄÜÖß ]',r'',b_text)
                        
                        #Select all the non-empty elements from the list
                        if c_text <> '' :
                            pure.append(c_text)           
                            #Update the value for files_dict dictionary with the final text
                            self.files_dict[k] = pure 
                                                           
        return self.files_dict
    
    def handle(self):
                
        _handlers = {'common': self.common_cmd,
                     'search': self.search_cmd}
        data = self.rfile.readline().strip()
        l = data.split()
        
        if len(l) >= 2:
            command, args = l[0], l[1:]
            f = _handlers.get(command, None)
            if f:
                ans = f(*args)
            else:
                ans = 'Invalid command'
        else:
            ans = 'Invalid Usage'
        
        self.request.sendall(ans + '\r\n')
        
    def common_cmd(self, *args):
        """Add your code here for the common command
        This function should return a string with the
        most n most common words in the books
        """
        self.create_dictionary_words()
        words = []
        
        for h in self.files_dict.values():    
            for q in range(len(h)):
                words.append(h[q])
        
        #Use Counter to find the n most common words
        words_to_count = (word for word in words if word[:1].isupper())
        c = Counter(words_to_count)
        f = dict(c.most_common(int(args[0])))

        for w in sorted(f, key=f.get, reverse=True):
            print w, f[w]

        ans = []
        
        return '\n'.join(ans)

    def search_cmd(self, *args):
        """Add your code here for the search command
        Should return a a string with the documents the
        word appears into"""
        
        self.create_dictionary_words()
        ans = []
        word_freq = {} #Dictionary where is stored the name of the file and how many times appears the 'word' in the file.
    
        for i,j in self.files_dict.iteritems():
        
            t = j.count(args[0])
            word_freq[i] = t
        
        #Sort the word_freq dictionary by value and number of appearances      
        word_items = [(v, k) for k, v in word_freq.items()]
        word_items.sort()
        word_items.reverse()             
        word_items = [(k, v) for v, k in word_items]
        
        for i in range(len(word_items)):
            
            print word_items[i][0],word_items[i][1]
                          
        return '\n'.join(ans)



if __name__ == '__main__':
    HOST, PORT = "0.0.0.0", 9999

    server = SocketServer.TCPServer((HOST, PORT), EchoRequestHandler)
    server.serve_forever()
