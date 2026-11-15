package main

import "fmt"

// Prueba léxica
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

	// Prueba sintáctica
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
	saludar()

	// Prueba semántica
	// Ámbitos: visitas y edad se declaran dentro de contarVisitas sin chocar con main
	contarVisitas()
}

// Tabla de símbolos con un ámbito por función. El mismo nombre puede declararse en
// funciones distintas sin que sea una redeclaración, y una función puede llamarse
// aunque esté declarada más abajo.
func contarVisitas() {
	var edad int = 30
	visitas := 1
	visitas = visitas + edad
	fmt.Println(visitas)
	saludar()
}
