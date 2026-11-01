package main

import "fmt"

// Función sin parámetros ni valor de retorno
func saludar() {
	fmt.Println("Hola Mundo")
}

func main() {
	// Declaración corta y reasignación
	contador := 1
	contador = 2
	mensaje := "Prueba léxica"

	// Variables con tipo explícito
	var edad int = 20
	var nombre string = "Ana"

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

	saludar()
}