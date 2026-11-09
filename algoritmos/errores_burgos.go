package main
import "fmt"
// Errores léxicos: números mal formados
func main() {
	a := 12abc
	b := 3.
	c := 3.14xyz
	fmt.Println(a, b, c)
}

// Errores sintácticos:
// Cada función contiene un error sintáctico distinto de las reglas de Burgos.

// Error 1: var exige un tipo explícito
func varSinTipo() {
	var edad = 20
}

// Error 2: el for con contador exige tres partes separadas por ;
func forIncompleto() {
	for i := 0; i < 10 {
		fmt.Println(i)
	}
}

// Error 3: falta el operando derecho de *
func faltaOperando() {
	total := 4 *
}

// Error 4: falta un argumento después de la coma
func faltaArgumento() {
	resultado := sumar(1, )
}

// Error 5: la condición del for está incompleta
func condicionFor() {
	for total < {
		total = total + 1
	}
}
// FIN aporte: BURGOS (errores sintácticos)