from builtins import range
import os
import sys
import re
import json
#import logging
import setup_paths
import numpy as np

from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
from nomadcore.parser_backend import JsonParseEventsWriterBackend
from contextlib import contextmanager

from libLibAtomsParser import *

try:
    from libMomo import osio, endl, flush
    osio.ConnectToFile('parser.osio.log')
    green = osio.mg
except:
    osio = endl = flush = None
    green = None

parser_info = {
    "name": "parser-lib-atoms", 
    "version": "0.0",
    "json": "../../../../nomad-meta-info/meta_info/nomad_meta_info/lib_atoms.nomadmetainfo.json"
}

# LOGGING
def log(msg, highlight=None, enter=endl):
    if osio:
        if highlight==None: hightlight = osio.ww
        osio << highlight << msg << enter
    return

# CONTEXT GUARD
@contextmanager
def open_section(p, name):
    gid = p.openSection(name)
    yield gid
    p.closeSection(name, gid)   

def push(jbe, terminal, key1, fct=lambda x: x.As(), key2=None):
    if key2 == None: key2 = key1
    value =  fct(terminal[key2])
    jbe.addValue(key1, value)
    return value

def push_array(jbe, terminal, key1, fct=lambda x: x.As(), key2=None):
    if key2 == None: key2 = key1
    value =  np.asarray(fct(terminal[key2]))
    jbe.addArrayValues(key1, value)
    return value

def push_value(jbe, value, key):
    jbe.addValue(key, value)
    return value

def push_array_values(jbe, value, key):
    jbe.addArrayValues(key, value)
    return value

def parse(output_file_name):
    jbe = JsonParseEventsWriterBackend(meta_info_env)
    jbe.startedParsingSession(output_file_name, parser_info)

    base_dir = os.path.dirname(os.path.abspath(output_file_name))
    terminal_gap = LibAtomsGapParser(osio)
    terminal_gap.ParseOutput(output_file_name)
    terminal_trj = terminal_gap.trj


    osio << "Start parsing ..." << osio.endl
    osio << "Base directory = '%s'" % base_dir << osio.endl

    gap = terminal_gap
    trj = terminal_trj

    with open_section(jbe, 'section_run') as gid_run:
        push(jbe, gap, 'program_name')
        push(jbe, gap, 'program_version', key2='GAP_params.svn_version')

    jbe.finishedParsingSession("ParseSuccess", None)
    return

if __name__ == '__main__':

    # CALCULATE PATH TO META-INFO FILE
    this_py_file = os.path.abspath(__file__)
    this_py_dirname = os.path.dirname(this_py_file)
    json_supp_file = parser_info["json"]
    meta_info_path = os.path.normpath(os.path.join(this_py_dirname, json_supp_file))

    # LOAD META-INFO FILE
    log("Meta-info from '%s'" % meta_info_path)
    meta_info_env, warns = loadJsonFile(
        filePath=meta_info_path,
        dependencyLoader=None,
        extraArgsHandling=InfoKindEl.ADD_EXTRA_ARGS,
        uri=None)

    output_file_name = sys.argv[1]
    parse(output_file_name)








