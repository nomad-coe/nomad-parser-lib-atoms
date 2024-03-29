#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
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

import pytest

from nomad.datamodel import EntryArchive
from libatomsparser import LibAtomsParser


def approx(value, abs=0, rel=1e-6):
    return pytest.approx(value, abs=abs, rel=rel)


@pytest.fixture(scope='module')
def parser():
    return LibAtomsParser()


def test_basic(parser):
    archive = EntryArchive()

    parser.parse('tests/data/gp.xml', archive, None)

    sec_run = archive.section_run[0]
    assert sec_run.program_version == 'svn_version="11610"'

    sec_systems = archive.section_run[0].section_system
    assert len(sec_systems) == 2000
    assert sec_systems[20].atom_labels[0] == 'W'
    assert sec_systems[1000].atom_positions[0][2].magnitude == 0.

    sec_sccs = sec_run.section_single_configuration_calculation
    assert len(sec_sccs) == 2000
    assert sec_sccs[30].energy_total.magnitude == approx(-1.77389589e-18)
