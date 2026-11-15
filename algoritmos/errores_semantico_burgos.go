package main

import "fmt"

// Operandos compatibles: se mezcla una cadena con un numero
func cadenaMasNumero() {
	total := "hola" + 5
}

// Operandos compatibles: int con float64
func enteroConFlotante() {
	a := 2
	b := 1.5
	c := a * b
}

// Operandos compatibles: entre cadenas solo se permite +
func restaDeCadenas() {
	d := "a" - "b"
}

// Operandos compatibles: % solo se permite entre enteros
func residuoFlotante() {
	r := 7.5 % 2.5
}

// Operandos compatibles: asignacion compuesta con tipos distintos
func compuestaMixta() {
	total := 10
	total += "cinco"
}

// Operandos compatibles: comparacion entre tipos distintos
func comparacionMixta() {
	edad := 20
	igual := edad == "veinte"
}

// Operandos compatibles: conector logico con numeros
func logicoConNumeros() {
	a := 1
	b := 2
	ok := a && b
}

// Operandos compatibles: negacion de un entero
func negacionDeNumero() {
	n := 5
	m := !n
}

// Operandos compatibles: signo negativo sobre una cadena
func signoEnCadena() {
	t := "hola"
	u := -t
}

// Operandos compatibles: incremento sobre una cadena
func incrementoEnCadena() {
	t := "hola"
	t++
}

// Operandos compatibles: indice fuera del rango del arreglo
func indiceFueraDeRango() {
	var notas [3]int
	x := notas[5]
}

// Retorno coherente: el return devuelve un tipo distinto al declarado
func retornoTipoDistinto() int {
	return "a"
}

// Retorno coherente: una funcion con retorno no incluye return
func sinReturn() int {
	x := 1
}

// Retorno coherente: return con valor en una funcion sin retorno
func retornaSinDeclarar() {
	return 1
}

// Retorno coherente: return sin valor en una funcion con retorno
func retornoVacio() int {
	return
}

func saludar() {
	fmt.Println("hola")
}

// Retorno coherente: se usa el valor de una funcion que no devuelve nada
func usarValorSinRetorno() {
	x := saludar()
}

// Correcto: operaciones y retornos validos
func sumar(a int, b int) int {
	return a + b
}

func operacionesValidas() {
	texto := "hola" + " mundo"
	entero := 7 % 2
	real := 1.5 * 2.0
	mayor := entero > 1
	r := sumar(2, 3)
	fmt.Println(texto, real, mayor, r)
}
