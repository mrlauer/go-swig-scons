package main

import (
	"clib/FirstTest"
	"fmt"
)

func main() {
	f := FirstTest.NewFoo()
	i := f.Fn()
	fmt.Printf("Magic number is %d\n", i)
	fmt.Printf("Magic number is %d\n", f.Bar())
}
