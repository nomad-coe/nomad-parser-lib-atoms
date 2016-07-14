from __future__ import print_function
from builtins import zip
from builtins import str
from builtins import map
from builtins import range
from builtins import object
import os
import sys
import re
import numpy as np

try:
    import ase
    import ase.io
    HAVE_ASE = True
except ImportError:
    HAVE_ASE = False
    pass

class LibAtomsParser(object):
    def __init__(self, log=None):
        self.log = log
        self.data = {}
        self.logtag = 'main'
        # KEY DEFAULT DICTIONARIES
        self.missing_keys_lh = [] # Transform keys that were not found in output
        self.missing_keys_rh = []
        self.ignored_keys = [] # Raw keys that did not have a transform
        self.keys_not_found = [] # Searches that failed
        return
    def __getitem__(self, key):
        self.selected_data_item = self.data[key]
        return self
    def As(self, typ=None):
        if typ == None:
            typ = type(self.selected_data_item)
        return typ(self.selected_data_item)
    def SummarizeKeyDefaults(self):
        if not self.log: return
        if len(self.missing_keys_lh):
            self.log << self.log.my \
                << "[%s] Keys from transformation maps that went unused (=> set to 'None'):" \
                % self.logtag << self.log.endl
            for lh, rh in zip(self.missing_keys_lh, self.missing_keys_rh):
                self.log << self.log.item << "Key = %-25s <> %25s" % (rh, lh) << self.log.endl
        if len(self.ignored_keys):
            self.log << self.log.mb \
                << "[%s] Keys from XY mapping that were not transformed (=> not stored):" \
                % self.logtag << self.log.endl
            for key in self.ignored_keys:
                self.log << self.log.item << "Key =" << key << self.log.endl
        if len(self.keys_not_found):
            self.log << self.log.mr \
                << "[%s] Keys from searches that failed (=> set to 'None'):" \
                % self.logtag << self.log.endl
            for key in self.keys_not_found:
                self.log << self.log.item << "Key =" << key << self.log.endl
        return
    def Set(self, key, value):
        if self.log:
            self.log << "Set [%s]   %-40s = %s" % (self.logtag, key, str(value)) << self.log.endl
        if key not in self.data:
            self.data[key] = value
        else:
            raise KeyError("Key already exists: '%s'" % key)
        return
    def SearchMapKeys(self, expr, ln, keys):
        s = re.search(expr, ln)
        try:
            for i in range(len(keys)):
                self.Set(keys[i], s.group(i+1).strip())
        except AttributeError:
            for i in range(len(keys)):
                self.Set(keys[i], None)
                self.keys_not_found.append(keys[i])
        return
    def ReadBlockXy(self, block):
        lns = block.lns
        block_data = {}
        for ln in lns:
            ln = ln.replace('\n','')
            if ln == '':
                continue
            if ':' in ln:
                sp = ln.split(':')
                x = sp[0].strip().split()
                y = sp[1].strip()
            elif '=' in ln:
                sp = ln.split('=')
                x = sp[0].strip().split()
                y = sp[1].strip()
            else:
                sp = ln.split()
                x = sp[:-1]
                y = sp[-1]
            key = ''
            for i in range(len(x)-1):                
                xi = x[i].replace('(','').replace(')','').lower()
                key += '%s_' % xi
            key += '%s' % x[-1].replace('(','').replace(')','').lower()
            value = y
            block_data[key] = value
        return block_data
    def ApplyBlockXyData(self, block_data, key_map):
        for key_in in key_map:
            key_out = key_map[key_in]            
            if key_in not in block_data:
                # Missing key in output
                self.missing_keys_lh.append(key_in)
                self.missing_keys_rh.append(key_out)
                value = None
            else:
                value = block_data[key_in]
            if key_out == None:
                key_out = key_in
            self.Set(key_out, value)
        for key in block_data:
            if key not in key_map:
                # Missing key in transform map
                self.ignored_keys.append(key)
        return
    def ParseOutput(self, output_file):        
        if self.log: 
            self.log << self.log.mg << "libAtomsParser::ParseOutput ..." << self.log.endl
        
        if HAVE_ASE:
            read_fct = ase.io.read
            read_fct_args = { 'index':':' }
        else:
            raise NotImplementedError("None-ASE read function requested, but not yet available.")
            read_fct = None
            read_fct_args = None

        # PARSE CONFIGURATIONS
        self.ase_configs = read_fct(output_file, **read_fct_args)
        for config in ase_configs:
            print(config)
        
        self.Set('program_name', 'libAtoms')
        self.Set('program_version', 'n/a')
        return

class LibAtomsTrajectory(LibAtomsParser):
    def __init__(self, log=None):
        super(LibAtomsTrajectory, self).__init__(log)
        self.ase_configs = None
        self.frames = []
    def ParseOutput(self, output_file):        
        if self.log: 
            self.log << self.log.mg << "libAtomsParser::ParseOutput ..." << self.log.endl
        
        if HAVE_ASE:
            read_fct = ase.io.read
            read_fct_args = { 'index':':' }
        else:
            raise NotImplementedError("None-ASE read function requested, but not yet available.")
            read_fct = None
            read_fct_args = None

        # PARSE CONFIGURATIONS
        self.ase_configs = read_fct(output_file, **read_fct_args)
        self.LoadAseConfigs(self.ase_configs)
        
        self.Set('program_name', 'libAtoms')
        self.Set('program_version', 'n/a')
        return
    def LoadAseConfigs(self, ase_configs):
        for config in ase_configs:
            frame = LibAtomsFrame(self.log)
            frame.LoadAseConfig(config)
            self.frames.append(frame)
        if self.log: log << "Loaded %d configurations" % len(self.frames) << log.endl
        return

class LibAtomsFrame(LibAtomsParser):
    def __init__(self, log=None):
        super(LibAtomsFrame, self).__init__(log)
        self.ase_config = None
    def LoadAseConfig(self, ase_config):
        self.ase_atoms = ase_config
        return

# ===================
# FILE & BLOCK STREAM
# ===================

class FileStream(object):
    def __init__(self, filename=None):
        if filename:
            self.ifs = open(filename, 'r')
        else:
            self.ifs = None
        return
    def SkipTo(self, expr):
        while True:
            ln = self.ifs.readline()
            if expr in ln:
                break
            if self.all_read():
                break
        return ln
    def SkipToMatch(self, expr):
        while True:            
            ln = self.ifs.readline()
            m = re.search(expr, ln)
            if m:
                return ln
            if self.all_read(): break
        return None
    def GetBlock(self, expr1, expr2):
        inside = False
        outside = False
        block = ''
        block_stream = BlockStream()
        while True:
            last_pos = self.ifs.tell()
            ln = self.ifs.readline()
            if expr1 in ln: inside = True
            if expr2 in ln: outside = True
            if inside and not outside:
                # Inside the block
                block += ln
                block_stream.append(ln)
            elif inside and outside:
                self.ifs.seek(last_pos)
                # Block finished
                break
            else:
                # Block not started yet
                pass
            if self.all_read(): break
        return block_stream  
    def GetBlockSequence(self, 
            expr_start, 
            expr_new, 
            expr_end, 
            remove_eol=True, 
            skip_empty=True):
        inside = False
        outside = False
        # Setup dictionary to collect blocks
        blocks = { expr_start : [] }
        for e in expr_new:
            blocks[e] = []
        # Assume structure like this (i <> inside, o <> outside)
        # Lines with 'i' get "eaten"
        # """
        # o ...
        # i <expr_start>
        # i ...
        # i <expr_new[1]>
        # i ...
        # i <expr_new[0]>
        # i ...
        # o <expr_end>
        # o ...
        # """
        key = None
        while True:
            # Log line position
            last_pos = self.ifs.tell()
            ln = self.ifs.readline()            
            # Figure out where we are
            if not inside and expr_start in ln:
                #print "Enter", expr_start
                inside = True
                key = expr_start
                new_block = BlockStream(key)
                blocks[key].append(new_block)
            for expr in expr_new:
                if inside and expr in ln:
                    #print "Enter", expr
                    key = expr
                    new_block = BlockStream(key)
                    blocks[key].append(new_block)
            if inside and expr_end != None and expr_end in ln:
                outside = True
            if inside and not outside:
                # Inside a block
                if remove_eol: ln = ln.replace('\n', '')
                if skip_empty and ln == '': pass
                else: blocks[key][-1].append(ln)
            elif inside and outside:
                # All blocks finished
                self.ifs.seek(last_pos)
                break
            else:
                # No blocks started yet
                pass
            if self.all_read(): break
        return blocks
    def all_read(self):
        return self.ifs.tell() == os.fstat(self.ifs.fileno()).st_size
    def readline(self):
        return ifs.readline()
    def close(self):
        self.ifs.close()
    def nextline(self):
        while True:
            ln = self.ifs.readline()
            if ln.strip() != '':
                return ln
            else: pass
            if self.all_read(): break
        return ln
    def ln(self):
        return self.nextline()
    def sp(self):
        return self.ln().split()
    def skip(self, n):
        for i in range(n):
            self.ln()
        return
    
class BlockStream(FileStream):
    def __init__(self, label=None):
        super(BlockStream, self).__init__(None)
        self.ifs = self
        self.lns = []
        self.idx = 0
        self.label = label
    def append(self, ln):
        self.lns.append(ln)
    def readline(self):
        if self.all_read():
            return ''        
        ln = self.lns[self.idx]
        self.idx += 1
        return ln
    def all_read(self):
        return self.idx > len(self.lns)-1
    def tell(self):
        return self.idx
    def cat(self, remove_eol=True, add_eol=False):
        cat = ''
        for ln in self.lns:
            if remove_eol:
                cat += ln.replace('\n', '')
            elif add_eol:
                cat += ln+'\n'
            else:
                cat += ln
        return cat
