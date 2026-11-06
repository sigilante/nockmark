-- l3build configuration for nockmark

module = "nockmark"

sourcefiledir = "tex"
docfiledir    = "doc"

sourcefiles  = {"*.sty"}
installfiles = {"*.sty"}
typesetfiles = {"nockmark.tex"}
textfiles    = {"README.md", "LICENSE"}

checkengines = {"pdftex", "xetex", "luatex"}
stdengine    = "pdftex"
