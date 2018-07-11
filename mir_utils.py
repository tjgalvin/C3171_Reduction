"""Utilities to help with the execution of miriad tasks and C3171 project data. 
"""

import subprocess as sp

primary = '1934-638'
secondary = '0327-241'
science = 'c3171'

chan_ref_7 = 6676 
flags_7 = {'chan_start':[7866-chan_ref_7, 8058-chan_ref_7, 8177-chan_ref_7, 7747-chan_ref_7, 1058, 670, 851, 788],
           'chan_end'  :[7896-chan_ref_7, 8088-chan_ref_7, 8207-chan_ref_7, 7777-chan_ref_7, 1065, 680, 857, 810]}

flags_9 = {'chan_start':[850],
           'chan_end'  :[900]}

# Known RFI ranges taken from the CABB sensitivity calculator
[[ 7747.0, 7777.0 ], [ 7866.0, 7896.0 ], [ 8058.0, 8088.0 ], [ 8177.0, 8207.0 ] ]

def uvflag(vis, flag_def):
    if len(flag_def['chan_start']) != len(flag_def['chan_end']):
        raise ValueError('Chanels star and end should have the same length')
        
    for start, end in zip(flag_def['chan_start'], flag_def['chan_end']):
        line = f"chan,{end-start},{start},1"
        print(line)
        proc = mirstr(f"uvflag vis={vis} line={line} flagval=flag").run()
        print(proc)

class mirstr(str):
    """Class to run a miriad task as a method call. Uses str as a base
    to make string printing easier. 

    TODO: make str addition i.e. a + b return a mirstr instance.
    """
    def __init__(self, *args, **kwargs):
        self.p = None
    
    def __str__(self):
        to_print = self
        
        if self.p is not None:
            to_print += self.p.stdout
            
        return to_print
    
    def run(self, *args, **kwargs):
        self.p = sp.run(self.split(), *args, stdout=sp.PIPE, stderr=sp.PIPE, **kwargs)
        self.p.stdout = self.p.stdout.decode()
        self.p.stderr = self.p.stderr.decode()
        
        if self.p.returncode:
            raise ValueError(self.p.stderr)
        
        return self
    
    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)
        
    def attribute(self, key):
        items = self.split()
        for i in items:
            if f"{key}=" in i:
                return i.split('=')[1]
        
        return None

    def __getattr__(self, name):
        """Assume this is miriad task related. It can be expanded further if
        needed to include header look ups, I guess. 
        
        Arguments:
            name {str} -- attribute from the miriad process str
        """
        try:
            val = self.attribute(name)
            if val is not None:
                return val
            
            raise AttributeError(name)

        except:
            raise AttributeError(name)



