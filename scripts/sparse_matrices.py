import numpy as np
import scipy
import scipy.sparse.linalg
from scipy.sparse import csr_matrix
from scipy import sparse as sp

class circuitMatrix():
    def __init__(self, size = 100):
        self.row = np.zeros(size)
        self.col = np.zeros(size)
        self.val = np.zeros(size)
        self.index = 0
        self.size = size
        self.sparse_matrix = None
        self.dense_matrix = None
        
    def add_element(self, i, j, val):
        self.row[self.index] = i
        self.col[self.index] = j
        self.val[self.index] = val
        self.index = self.index + 1
        
        if (self.index >= size):
            self.widen_vectors(1)
        
    def widen_vectors(self, amount):
        self.row = np.hstack((self.row, amount * [0]))
        self.col = np.hstack((self.col, amount * [0]))
        self.val = np.hstack((self.val, amount * [0]))
            
    def generate_matrix_from_sparse(self):
        self.sparse_matrix = csr_matrix((self.val, (self.row, self.col)), 
                                        shape = (self.size, self.size)).toarray()
        
    def to_dense(self):
        if (self.sparse_matrix == None):
            return np.zeros((size, size))
        else:
            return self.sparse_matrix.todense()