package main

// Errores léxicos: números mal formados
func main() {
	a := 12abc
	b := 3.
	c := 3.14xyz
	fmt.Println(a, b, c)
}
