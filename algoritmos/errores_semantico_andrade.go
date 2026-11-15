package main

import "fmt"

// Inexistencia: se usa una variable que nunca se declaro
func usoSinDeclarar() {
	y = 10
}

// Inexistencia: variable no declarada dentro de una expresion
func usoEnExpresion() {
	total := puntos + 1
}

// Inexistencia: se llama a una funcion que no existe
func llamadaSinFuncion() {
	calcularTotal()
}

// Duplicidad: redeclaracion con var en el mismo ambito
func redeclaracionVar() {
	var x int = 1
	var x string = "dos"
}

// Duplicidad: redeclaracion con := en el mismo ambito
func redeclaracionCorta() {
	a := 1
	a := 2
}

// Duplicidad: una funcion declarada dos veces
func repetida() {
	fmt.Println("uno")
}

func repetida() {
	fmt.Println("dos")
}

// Inexistencia: el nombre de una funcion se usa como si fuera una variable
func funcionComoVariable() {
	resultado := usoSinDeclarar
}

// Inexistencia: una variable se llama como si fuera una funcion
func variableComoFuncion() {
	contador := 1
	contador()
}

// Inexistencia: una variable declarada dentro de un bloque no existe fuera de el
func fueraDelBloque() {
	if true {
		interna := 1
	}
	interna = 2
}

// Correcto: el mismo nombre en bloques distintos no es una redeclaracion
func bloquesDistintos() {
	for i := 0; i < 3; i++ {
		fmt.Println(i)
	}
	for i := 0; i < 3; i++ {
		fmt.Println(i)
	}
}
