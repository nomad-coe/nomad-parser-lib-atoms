# Copyright 2016-2018 Fawzi Mohamed, Carl Poelking, Daria Tomecka
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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
import xml.dom.minidom
from nomad.utils import create_uuid

try:
    import ase
    import ase.io
    HAVE_ASE = True
except ImportError:
    HAVE_ASE = False
    pass

def XmlGetUnique(root, tag):
    nodes = XmlGetAll(root, tag)
    if len(nodes) > 1:
        raise ValueError("More than one node with tag '%s'" % tag)
    return nodes[0]

def XmlGetAll(root, tag):
    nodes = root.getElementsByTagName(tag)
    ret_nodes = []
    for node in nodes:
        if node.localName != None: ret_nodes.append(node)
    return ret_nodes

def XmlGetChildDict(root):
    tag_child = {}
    for child in root.childNodes:
        if child.localName == None: continue
        if not child.localName in tag_child:
            tag_child[child.localName] = []
        tag_child[child.localName].append(child)
    return tag_child

def XmlGetAttributes(root):
    return root.attributes

def XmlGetText(root):
    return root.firstChild.nodeValue



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
            return self.selected_data_item
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
        # for config in ase_configs:
        #     print(config)

        self.Set('program_name', 'libAtoms')
        self.Set('program_version', 'n/a')
        return

class LibAtomsGapParser(LibAtomsParser):
    def __init__(self, log=None):
        super(LibAtomsGapParser, self).__init__(log)
        self.logtag = 'gap-xml'
        self.trj = None
        self.has_gap_data = False
        return
    def ParseOutput(self, output_file, base_dir=''):
        self.Set('program_name', 'libAtoms')
        dom = xml.dom.minidom.parse(output_file)
        root = XmlGetUnique(dom, 'GAP_params')
        # Child keys should be: ['gpSparse', 'command_line', 'GAP_data', 'XYZ_data']
        # print(list(child_nodes.keys()))
        child_nodes = XmlGetChildDict(root)

        # 'GAP_params'
        atts = XmlGetAttributes(root)
        keys = ['label', 'svn_version']
        for key in keys:
            self.Set('GAP_params.%s' % key, atts[key].value) # TODO Handle look-up errors

        # 'GAP_params/GAP_data'
        key = 'GAP_data'
        if key in child_nodes:
            node = child_nodes[key][0]
            atts = XmlGetAttributes(node)
            keys = ['do_core', 'e0']
            for key in keys:
                self.Set('GAP_data.%s' % key, atts[key].value) # TODO Handle look-up errors

        # 'GAP_params/command_line'
        key = 'command_line'
        if key in child_nodes:
            node = child_nodes[key][0]
            text = XmlGetText(node)
            self.Set('command_line.command_line', text)

        # 'GAP_params/gpSparse'
        key = 'gpSparse'
        if key in child_nodes:
            self.has_gap_data = True
            node = child_nodes[key][0]
            atts = XmlGetAttributes(node)
            keys = ['n_coordinate']
            for key in keys:
                self.Set('gpSparse.%s' % key, atts[key].value) # TODO Handle look-up errors

            # GAP_params/gpSparse/gpCoordinates
            gp_coord_node = XmlGetUnique(node, 'gpCoordinates')
            gp_coord_child_nodes = XmlGetChildDict(gp_coord_node)
            gp_coord_node_att = XmlGetAttributes(gp_coord_node)
            for key in gp_coord_node_att.keys():
                self.Set('gpCoordinates.%s' % key, gp_coord_node_att[key].value)

            # 'GAP_params/gpSparse/gpCoordinates/theta
            key = 'theta'
            if key in gp_coord_child_nodes:
                node = gp_coord_child_nodes[key][0]
                text = XmlGetText(node).strip()
                self.Set('gpCoordinates.%s' % key, text)
            # 'GAP_params/gpSparse/gpCoordinates/descriptor
            key = 'descriptor'
            if key in gp_coord_child_nodes:
                node = gp_coord_child_nodes[key][0]
                text = XmlGetText(node).strip()
                self.Set('gpCoordinates.%s' % key, text)
            # 'GAP_params/gpSparse/gpCoordinates/descriptor
            key = 'permutation'
            if key in gp_coord_child_nodes:
                node = gp_coord_child_nodes[key][0]
                att = XmlGetAttributes(node)
                text = XmlGetText(node).strip()
                self.Set('gpCoordinates.perm.%s' % key, text)
                self.Set('gpCoordinates.perm.i', att['i'].value)
            # 'GAP_params/gpSparse/gpCoordinates/sparseX
            key = 'sparseX'
            if key in gp_coord_child_nodes:
                n_sparseX = self['gpCoordinates.n_sparseX'].As(int)
                n_dim = self['gpCoordinates.dimensions'].As(int)
                sparseX_filename = self['gpCoordinates.sparseX_filename'].As(str)
                sparseX_filename = os.path.join(base_dir, sparseX_filename)
                # Read alpha coefficients
                nodes = gp_coord_child_nodes[key]
                alpha_cutoff = np.zeros((n_sparseX, 2), dtype='float64')
                for i,node in enumerate(nodes):
                    att = XmlGetAttributes(node)
                    alpha_cutoff[i,0] = float(att["alpha"].value)
                    alpha_cutoff[i,1] = float(att["sparseCutoff"].value)
                self.Set('gpCoordinates.alpha', alpha_cutoff)
                # Read descriptor matrix
                X_matrix = np.loadtxt(sparseX_filename)
                assert X_matrix.shape[0] == n_sparseX*n_dim
                # i-th row of X-matrix stores X-vector of config i
                X_matrix = X_matrix.reshape((n_dim, n_sparseX))
                self.Set('gpCoordinates.sparseX', X_matrix)

        # 'GAP_params/XYZ_data'
        key = 'XYZ_data'
        if key in child_nodes:
            node = child_nodes[key][0]
            text = XmlGetText(node)
            unique_ID = create_uuid()
            trj_file = '/tmp/' + unique_ID + '-lib-atoms-gap.from-xml.xyz'
            ofs = open(trj_file, 'w')
            for child in node.childNodes:
                if child.nodeValue == None: continue
                ln = child.nodeValue.strip(' \n')
                if ln == '': continue
                ofs.write(ln+'\n')
            ofs.close()
            self.trj = LibAtomsTrajectory(self.log)
            self.trj.ParseOutput(trj_file)
        return

class LibAtomsTrajectory(LibAtomsParser):
    def __init__(self, log=None):
        super(LibAtomsTrajectory, self).__init__(log)
        self.ase_configs = None
        self.frames = []
        self.logtag = 'trj'
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
        if self.log: self.log << "Loaded %d configurations" % len(self.frames) << self.log.endl
        return

class LibAtomsFrame(LibAtomsParser):
    def __init__(self, log=None):
        super(LibAtomsFrame, self).__init__(log)
        self.ase_config = None
        self.has_energy = False
        self.energy = None
        self.has_virial = False
        self.virial = None
        self.has_config_type = False
        self.config_type = None
    def LoadAseConfig(self, ase_config):
        self.ase_config = ase_config
        # print("INFO", self.ase_config.info)
        key = 'energy'
        if key in self.ase_config.info:
            self.has_energy = True
            self.energy = self.ase_config.info[key]
        else:
            self.has_energy = True
            self.energy = self.ase_config.get_total_energy()
        key = 'config_type'
        if key in self.ase_config.info:
            self.has_config_type = True
            self.config_type = self.ase_config.info[key]
        key = 'virial'
        if key in self.ase_config.info:
            self.has_virial = True
            self.virial = np.array(self.ase_config.info[key])
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
