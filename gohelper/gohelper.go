package main

import (
	"go/ast"
	"go/parser"
	"go/token"
	"io"
	"log"
	"strings"
	"fmt"
	"flag"
	"os"
	"runtime"
)

type walker struct {
	Deps []string
}

func (w *walker) Visit(node ast.Node) ast.Visitor {
	switch n := node.(type) {
	case *ast.ImportSpec:
		w.Deps = append(w.Deps, strings.Trim(n.Path.Value, `"`))
		return nil
	}
	return w
}

func FindDeps(reader io.Reader) ([]string, error) {
	tree, err := parser.ParseFile(token.NewFileSet(), "filename", reader, parser.ImportsOnly)
	if err != nil {
		return nil, err
	}

	var w walker
	ast.Walk(&w, tree)

	return w.Deps, nil
}

func PrintDeps(reader io.Reader, writer io.Writer) {
	deps, err := FindDeps(reader)
	if err != nil {
		log.Fatal("Could not parse file imports")
	}

	for _, l := range deps {
		fmt.Fprintln(writer, l)
	}
}

func PrintVariables(writer io.Writer) {
	fmt.Fprintf(writer, "GOOS=%s\n", runtime.GOOS)
	fmt.Fprintf(writer, "GOARCH=%s\n", runtime.GOARCH)
	fmt.Fprintf(writer, "GOROOT=%s\n", runtime.GOROOT())
	var ArchChar string
	switch runtime.GOARCH {
	case "amd64":
		ArchChar = "6"
	case "386":
		ArchChar = "8"
	default:
		ArchChar = "5"
	}
	fmt.Fprintf(writer, "GOARCHCHAR=%s\n", ArchChar)
}

func main() {
	deps := flag.Bool("deps", false, "compute dependencies")
	govars := flag.Bool("govars", false, "print go variables")
	flag.Parse()

	if *deps {
		PrintDeps(os.Stdin, os.Stdout)
	}
	if *govars {
		PrintVariables(os.Stdout)
	}
}
