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
  mainFileTypes = Seq("text/.*"),
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
