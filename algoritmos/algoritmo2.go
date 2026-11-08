package main

import "fmt"

/* Algoritmo de prueba 2 - Integrante: Burgos
   Cubre: var, const, for, break, return, float64, literal flotante,
   matriz, operadores aritméticos (+ - * / %), operadores de comparación
   (== != < <= > >=) y el delimitador ; */

// Función con un valor de retorno
func sumar(a int, b int) int {
	return a + b
}

func promedio(a float64, b float64) float64 {
	return (a + b) / 2.0
}

func main() {
	// Constantes y variables con tipo explícito
	const MAX int = 100
	const PI float64 = 3.14
	var total int = 0
	var precio float64 = 20.5
	var resto int

	// Operadores aritméticos
	producto := 6 * 7
	cociente := producto / 2
	resto = 17 % 5
	diferencia := cociente - resto
	area := PI * precio * precio

	// Operadores de comparación
	igual := total == 0
	distinto := total != MAX
	menor := total < MAX
	menorIgual := total <= MAX
	mayor := precio > 10.5
	mayorIgual := precio >= 20.5

	// for con contador (usa ;) y break
	for i := 0; i < 10; i++ {
		if i == 7 {
			break
		}
		total = total + i
	}

	// for con condición
	for total < 100 {
		total = total + 5
	}

	// Matriz de 2x2
	var tablero [2][2]int
	tablero[0][0] = 1
	matriz := [2][2]int{{1, 2}, {3, 4}}

		// Sintáctico
	// Operaciones * / % encadenadas, llamada con retorno en una declaración,
	// var sin valor inicial y for con contador distinto (j)
	mixto := producto * 2 / 4 % 3
	suma := sumar(2, 3)
	var vacio float64
	for j := 0; j < 3; j++ {
		suma = suma + j
	}
	fmt.Println("Suma", suma, mixto, vacio)
	// FIN sintáctico

	fmt.Println(igual, distinto, menor, menorIgual, mayor, mayorIgual)
	fmt.Println(sumar(total, resto), promedio(precio, 3.5))
	fmt.Println(MAX, diferencia, area, tablero[0][0], matriz[1][1])
}
