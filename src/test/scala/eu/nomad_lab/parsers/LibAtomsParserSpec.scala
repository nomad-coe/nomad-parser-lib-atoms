package eu.nomad_lab.parsers

import org.specs2.mutable.Specification

object LibAtomsParserSpec extends Specification {
  "LibAtomsParserTest" >> {
    "test with json-events" >> {
      ParserRun.parse(LibAtomsParser, "parsers/lib-atoms/test/lib-atoms-gap-test/gp.xml", "json-events") must_== ParseResult.ParseSuccess
    }
    "test with json" >> {
      ParserRun.parse(LibAtomsParser, "parsers/lib-atoms/test/lib-atoms-gap-test/gp.xml", "json") must_== ParseResult.ParseSuccess
    }
  }
}
