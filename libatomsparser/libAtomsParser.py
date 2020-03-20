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

from builtins import range
import os
import sys
import re
import json
import logging
# import setup_paths
import numpy as np

from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
from contextlib import contextmanager

from libatomsparser.libLibAtomsParser import *

# try:
#     from libMomo import osio, endl, flush
#     osio.ConnectToFile('parser.osio.log')
#     green = osio.mg
# except:
osio = endl = flush = None
green = None

parser_info = {
    "name": "parser-lib-atoms",
    "version": "0.0",
    "json": "../../../../nomad-meta-info/meta_info/nomad_meta_info/lib_atoms.nomadmetainfo.json"
}


class LibAtomsParserWrapper():
    """ A proper class envolop for running this parser using Noamd-FAIRD infra. """
    def __init__(self, backend, **kwargs):
        self.backend_factory = backend

    def parse(self, mainfile):
        logging.info('lib-atoms parser started')
        logging.getLogger('nomadcore').setLevel(logging.WARNING)
        backend = self.backend_factory("lib_atoms.nomadmetainfo.json")
        # Call the old parser without a class.
        parserInfo = {'name': 'lib_atoms-parser', 'version': '0.0'}
        backend = parse_without_class(mainfile, backend, parserInfo)
        return backend


# LOGGING
def log(msg, highlight=None, enter=endl):
    # if osio:
    #     if highlight==None: hightlight = osio.ww
    #     osio << highlight << msg << enter
    logging.debug(msg)
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

def parse_without_class(output_file_name, backend, parser_info):
    """ Parse method to parse mainfile and write output to backend."""
    jbe = backend
    jbe.startedParsingSession(output_file_name, parser_info)
    base_dir = os.path.dirname(os.path.abspath(output_file_name))

    # jbe.startedParsingSession(output_file_name, parser_info)

    # base_dir = os.path.dirname(os.path.abspath(output_file_name))
    terminal_gap = LibAtomsGapParser(osio)
    terminal_gap.ParseOutput(output_file_name, base_dir)
    terminal_trj = terminal_gap.trj

    logging.debug("Start parsing...")
    # osio << "Start parsing ..." << osio.endl
    logging.debug('Base directory = %s' % base_dir)
    # osio << "Base directory = '%s'" % base_dir << osio.endl

    gap = terminal_gap
    trj = terminal_trj

    length_libatoms2nomad = 1e-10 # angstrom to meter
    energy_libatoms2nomad = 1.60217662e-19

    with open_section(jbe, 'section_run') as gid_run:
        push(jbe, gap, 'program_name')
        push(jbe, gap, 'program_version', key2='GAP_params.svn_version')

        # SYSTEM DESCRIPTION
        refs_system_description = []
        all_frames = trj.frames # <- Initial config + trajectory
        for frame in all_frames:
            with open_section(jbe, 'section_system') as gid:
                refs_system_description.append(gid)
                # Configuration core
                atom_labels = np.array(frame.ase_config.get_chemical_symbols())
                push_array_values(jbe, atom_labels, 'atom_labels')
                push_array_values(jbe, frame.ase_config.get_positions()*length_libatoms2nomad, 'atom_positions')
                # CAREFUL, OBSERVE CELL CONVENTION: 1st index -> x,y,z, 2nd index -> a,b,c
                # Hence use transpose here:
                push_array_values(jbe, frame.ase_config.get_cell().T*length_libatoms2nomad, 'simulation_cell')
                push_array_values(jbe, frame.ase_config.get_pbc(), 'configuration_periodic_dimensions')
                if frame.ase_config.has('velocities'):
                    push_array_values(jbe, frame.ase_config.get_velocities()*length_libatoms2nomad, 'atom_velocities')
                if frame.ase_config.has('forces'):
                    # TODO Wouldn't it be nicer if forces were added here?
                    pass
                pass

        # SINGLE CONFIGURATIONS
        refs_single_configuration = []
        i_frame = -1
        for frame in all_frames:
            i_frame += 1
            with open_section(jbe, 'section_single_configuration_calculation') as gid:
                refs_single_configuration.append(gid)
                # Reference system description section
                ref_system = refs_system_description[i_frame]
                push_value(jbe, ref_system, 'single_configuration_calculation_to_system_ref')
                # Energy
                if frame.has_energy:
                    push_value(jbe, frame.energy*energy_libatoms2nomad, 'energy_total') # TODO Check units
                # Virial
                if frame.has_virial:
                    push_array_values(jbe, frame.virial, 'x_lib_atoms_virial_tensor')
                # Forces
                if frame.ase_config.has('forces'):
                    push_array_values(jbe, frame.ase_config.get_forces(), 'atom_forces')
                # Type label
                if frame.has_config_type:
                    push_value(jbe, frame.config_type, 'x_lib_atoms_config_type')
                pass

        # FRAME SEQUENCE
        with open_section(jbe, 'section_frame_sequence'):
            push_value(jbe, len(all_frames), 'number_of_frames_in_sequence')
            refs_config = np.array(refs_single_configuration)
            push_array_values(jbe, refs_config, 'frame_sequence_local_frames_ref')

        # GAP DESCRIPTION
        if gap.has_gap_data:
            with open_section(jbe, 'x_lib_atoms_section_gap') as gap_gid:
                push_array_values(jbe, np.array(refs_single_configuration), 'x_lib_atoms_training_config_refs')
                push_value(jbe, gap['GAP_params.label'].As(), 'x_lib_atoms_GAP_params_label')
                push_value(jbe, gap['GAP_params.svn_version'].As(), 'x_lib_atoms_GAP_params_svn_version')
                push_value(jbe, gap['GAP_data.do_core'].As(), 'x_lib_atoms_GAP_data_do_core')
                push_value(jbe, gap['GAP_data.e0'].As(float), 'x_lib_atoms_GAP_data_e0')
                push_value(jbe, gap['command_line.command_line'].As(), 'x_lib_atoms_command_line_command_line')
                push_value(jbe, gap['gpSparse.n_coordinate'].As(int), 'x_lib_atoms_gpSparse_n_coordinate')
                types = [int,         int,          int,              str,          float,             float,         float,             str,     str,                float,   str,          int,                int ]
                keys  = ['n_sparseX', 'dimensions', 'n_permutations', 'sparsified', 'signal_variance', 'signal_mean', 'covariance_type', 'label', 'sparseX_filename', 'theta', 'descriptor', 'perm.permutation', 'perm.i']
                for i,key in enumerate(keys):
                    push_value(jbe, gap['gpCoordinates.%s' % key].As(types[i]), 'x_lib_atoms_gpCoordinates_%s' % key.replace('.', '_'))
                for key in ['alpha', 'sparseX']:
                    push_array_values(jbe, gap['gpCoordinates.%s' % key].As(), 'x_lib_atoms_gpCoordinates_%s' % key.replace('.', '_'))

    jbe.finishedParsingSession("ParseSuccess", None)
    return jbe

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








