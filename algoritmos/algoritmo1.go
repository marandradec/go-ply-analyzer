package main

import "fmt"

// INICIO lexico
// Función sin parámetros ni valor de retorno
func saludar() {
	fmt.Println("Hola Mundo")
}

func main() {
	// Declaración corta y reasignación
	contador := 1
	contador = 2
	mensaje := "Prueba léxica"

	/* Comentario de varias líneas:
	   a partir de aquí se declaran las variables
	   con tipo explícito y los arreglos */

	// Variables con tipo explícito
	var edad int = 20
	var nombre string = "Ana"

	// Operaciones aritméticas
	suma := edad + contador
	resta := suma - 1

	// Comparaciones de igualdad
	esIgual := contador == 2
	esDistinto := edad != 18

	// Arreglo de tamaño fijo
	var notas [3]int
	notas[0] = 15
	primos := [3]int{2, 3, 5}

	// Condicional
	if edad > 18 {
		fmt.Println(mensaje)
	} else {
		fmt.Println(nombre)
	}

	fmt.Println(resta, esIgual, esDistinto)
	// FIN lexico

	// INICIO sintáctico
	// Suma y resta encadenadas, acceso a arreglo dentro de una expresión
	calculo := edad + contador - 1
	primero := notas[0] + primos[1]
	// if / else if / else y llamada a función sin parámetros
	if calculo > 30 {
		fmt.Println("alto")
	} else if calculo == 30 {
		fmt.Println("medio")
	} else {
		fmt.Println("bajo")
	}
	fmt.Println(primero)
	// FIN sintáctico
	saludar()
}
