import numpy as np
import scipy
import scipy.sparse.linalg
from scipy.sparse import csr_matrix
from scipy import sparse as sp
import parse

class sparse_row():
    def __init__(self, master, row):
        self.master = master
        self.row = row
    
    def __setitem__(self, idx, value):
        self.master.add_element(self.row, idx, value)
        
    def __getitem__(self, idx):
        self.master.added_items["{},{}".format(self.row,idx)] = 0 
        return self.master.added_items["{},{}".format(self.row,idx)]
        
        
    
class sparse_matrix():
    def __init__(self, size = 100):
        self.row = np.zeros(size)
        self.col = np.zeros(size)
        self.val = np.zeros(size)
        self.index = 0
        self.size = size
        self.entries_row = {}
        self.added_items = {}
        self.sparse_matrix = csr_matrix((self.val, (self.row, self.col)), 
                                        shape = (self.size, self.size))
        
    def __getitem__(self,idx):
        return sparse_row(self,idx)
        
    def add_element(self, i, j, val):
        self.row[self.index] = i
        self.col[self.index] = j
        self.val[self.index] = val
        self.index = self.index + 1
        
        if (self.index >= self.size):
            self.widen_vectors(1)
        
    def widen_vectors(self, amount):
        self.row = np.hstack((self.row, amount * [0]))
        self.col = np.hstack((self.col, amount * [0]))
        self.val = np.hstack((self.val, amount * [0]))
            
    def generate_matrix_from_sparse(self):
        for key in self.added_items.keys():
            parsed = parse.parse("{},{}", key)
            print("parsed",parsed[0],parsed[1])
        self.sparse_matrix = csr_matrix((self.val, (self.row, self.col)), 
                                        shape = (self.size, self.size))
        
    def to_dense(self):
        if (self.sparse_matrix == None):
            return np.zeros((size, size))
        else:
            return self.sparse_matrix.todense()
        
if __name__ == "__main__":
    print("np operators", dir(np.ones((2,2))))
    print("test")
    s = sparse_matrix()
    s[4][5] += 5
    s.generate_matrix_from_sparse()
    print(s.sparse_matrix)
    print("s",s)
    print("row",s.sparse_matrix.getrow(4).toarray())