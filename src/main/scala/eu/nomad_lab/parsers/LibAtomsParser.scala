/*
 * Copyright 2016-2018 Fawzi Mohamed, Carl Poelking, Daria Tomecka
 * 
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 */

package eu.nomad_lab.parsers

import eu.{ nomad_lab => lab }
import eu.nomad_lab.DefaultPythonInterpreter
import org.{ json4s => jn }
import scala.collection.breakOut

object LibAtomsParser extends SimpleExternalParserGenerator(
  name = "LibAtomsParser",
  parserInfo = jn.JObject(
    ("name" -> jn.JString("LibAtomsParser")) ::
      ("parserId" -> jn.JString("LibAtomsParser" + lab.LibAtomsVersionInfo.version)) ::
      ("versionInfo" -> jn.JObject(
        ("nomadCoreVersion" -> jn.JObject(lab.NomadCoreVersionInfo.toMap.map {
          case (k, v) => k -> jn.JString(v.toString)
        }(breakOut): List[(String, jn.JString)])) ::
          (lab.LibAtomsVersionInfo.toMap.map {
            case (key, value) =>
              (key -> jn.JString(value.toString))
          }(breakOut): List[(String, jn.JString)])
      )) :: Nil
  ),
  mainFileTypes = Seq("application/xml"),
  mainFileRe = """\s*<GAP_params\s""".r,
  cmd = Seq(DefaultPythonInterpreter.pythonExe(), "${envDir}/parsers/lib-atoms/parser/parser-lib-atoms/libAtomsParser.py",
    "${mainFilePath}"),
  resList = Seq(
    "parser-lib-atoms/libAtomsParser.py",
    "parser-lib-atoms/libLibAtomsParser.py",
    "parser-lib-atoms/libMomo.py",
    "parser-lib-atoms/setup_paths.py",
    "nomad_meta_info/public.nomadmetainfo.json",
    "nomad_meta_info/common.nomadmetainfo.json",
    "nomad_meta_info/meta_types.nomadmetainfo.json",
    "nomad_meta_info/lib_atoms.nomadmetainfo.json"
  ) ++ DefaultPythonInterpreter.commonFiles(),
  dirMap = Map(
    "parser-lib-atoms" -> "parsers/lib-atoms/parser/parser-lib-atoms",
    "nomad_meta_info" -> "nomad-meta-info/meta_info/nomad_meta_info"
  ) ++ DefaultPythonInterpreter.commonDirMapping()
)
