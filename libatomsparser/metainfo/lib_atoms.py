#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD.
# See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import numpy as np            # pylint: disable=unused-import
import typing                 # pylint: disable=unused-import
from nomad.metainfo import (  # pylint: disable=unused-import
    MSection, MCategory, Category, Package, Quantity, Section, SubSection, SectionProxy,
    Reference
)
from nomad.metainfo.legacy import LegacyDefinition

from nomad.datamodel.metainfo import public

m_package = Package(
    name='lib_atoms_nomadmetainfo_json',
    description='None',
    a_legacy=LegacyDefinition(name='lib_atoms.nomadmetainfo.json'))


class x_lib_atoms_section_gap(MSection):
    '''
    Description of Gaussian Approximation Potentials (GAPs).
    '''

    m_def = Section(validate=False, a_legacy=LegacyDefinition(name='x_lib_atoms_section_gap'))

    x_lib_atoms_training_config_refs = Quantity(
        type=public.section_single_configuration_calculation,
        shape=['n_sparseX'],
        description='''
        References to frames in training configuration.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_training_config_refs'))

    x_lib_atoms_GAP_params_label = Quantity(
        type=str,
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_GAP_params_label'))

    x_lib_atoms_GAP_params_svn_version = Quantity(
        type=str,
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_GAP_params_svn_version'))

    x_lib_atoms_GAP_data_do_core = Quantity(
        type=str,
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_GAP_data_do_core'))

    x_lib_atoms_GAP_data_e0 = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_GAP_data_e0'))

    x_lib_atoms_command_line_command_line = Quantity(
        type=str,
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_command_line_command_line'))

    x_lib_atoms_gpSparse_n_coordinate = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpSparse_n_coordinate'))

    x_lib_atoms_gpCoordinates_n_permutations = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_n_permutations'))

    x_lib_atoms_gpCoordinates_sparsified = Quantity(
        type=str,
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_sparsified'))

    x_lib_atoms_gpCoordinates_signal_variance = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_signal_variance'))

    x_lib_atoms_gpCoordinates_label = Quantity(
        type=str,
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_label'))

    x_lib_atoms_gpCoordinates_n_sparseX = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_n_sparseX'))

    x_lib_atoms_gpCoordinates_covariance_type = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_covariance_type'))

    x_lib_atoms_gpCoordinates_signal_mean = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_signal_mean'))

    x_lib_atoms_gpCoordinates_sparseX_filename = Quantity(
        type=str,
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_sparseX_filename'))

    x_lib_atoms_gpCoordinates_dimensions = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_dimensions'))

    x_lib_atoms_gpCoordinates_theta = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_theta'))

    x_lib_atoms_gpCoordinates_descriptor = Quantity(
        type=str,
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_descriptor'))

    x_lib_atoms_gpCoordinates_perm_permutation = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_perm_permutation'))

    x_lib_atoms_gpCoordinates_perm_i = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_perm_i'))

    x_lib_atoms_gpCoordinates_alpha = Quantity(
        type=np.dtype(np.float64),
        shape=['n_sparseX', 2],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_alpha'))

    x_lib_atoms_gpCoordinates_sparseX = Quantity(
        type=np.dtype(np.float64),
        shape=['n_sparseX', 'dimensions'],
        description='''
        GAP classifier.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_gpCoordinates_sparseX'))


class section_run(public.section_run):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_run'))

    x_lib_atoms_section_gap = SubSection(
        sub_section=SectionProxy('x_lib_atoms_section_gap'),
        repeats=False,
        a_legacy=LegacyDefinition(name='x_lib_atoms_section_gap'))


class section_single_configuration_calculation(public.section_single_configuration_calculation):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_single_configuration_calculation'))

    x_lib_atoms_virial_tensor = Quantity(
        type=np.dtype(np.float64),
        shape=[3, 3],
        unit='pascal',
        description='''
        Virial tensor for this frame.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_virial_tensor'))

    x_lib_atoms_config_type = Quantity(
        type=str,
        shape=[],
        description='''
        Configuration type, e.g. = dislocation_quadrupole.
        ''',
        a_legacy=LegacyDefinition(name='x_lib_atoms_config_type'))


m_package.__init_metainfo__()
