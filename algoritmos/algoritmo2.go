package main

import "fmt"

/* Algoritmo de prueba 2 - Integrante: Burgos
   Cubre: var, const, for, break, return, float64, literal flotante,
   matriz, operadores aritméticos (+ - * / %), operadores de comparación
   (== != < <= > >=) y el delimitador ;
    Semántico (reglas de Burgos): operandos compatibles y retorno coherente */

// Función con un valor de retorno
func sumar(a int, b int) int {
	return a + b
}

func promedio(a float64, b float64) float64 {
	return (a + b) / 2.0
}

// Semántico (Burgos): retorno coherente
// El tipo de cada return coincide con el que declara la función y toda función
// con tipo de retorno incluye al menos un return
func nombreCompleto(nombre string, apellido string) string {
	return nombre + " " + apellido
}

func esPar(numero int) bool {
	return numero%2 == 0
}

func mayorDe(a int, b int) int {
	if a > b {
		return a
	}
	return b
}

func areaTriangulo(base float64, altura float64) float64 {
	return base * altura / 2.0
}

// Una función sin tipo de retorno puede usar return sin valor
func avisar(limite int, valor int) {
	if valor > limite {
		fmt.Println("Excede el limite")
		return
	}
	fmt.Println("Dentro del limite")
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

	// Semántico (Burgos): operandos compatibles
	// Aritmética entre operandos numéricos del mismo tipo (% solo entre enteros)
	unidades := 12
	lotes := 5
	totalUnidades := unidades + lotes
	sobrante := unidades % lotes
	peso := 7.5
	factor := 2.5
	pesoTotal := peso * factor
	pesoMedio := peso / factor
	negado := -peso
	bonoMax := MAX % 7
	mitadPI := PI / 2.0
	lotes++
	totalUnidades += lotes
	sobrante -= 1

	// + entre dos cadenas concatena
	saludo := "Hola" + " " + "Go"
	saludo += "!"
	completo := nombreCompleto("Ana", "Perez")
	etiqueta := completo + ": " + saludo

	// Comparaciones entre operandos del mismo tipo y conectores entre booleanos
	mismoTexto := completo == "Ana Perez"
	antes := "ana" < "luis"
	pesado := peso >= factor
	enRango := unidades > 0 && lotes < 10
	fueraDeRango := !enRango

	// Índices enteros dentro del rango de la matriz
	pos := 1
	elemento := matriz[pos][0] + tablero[0][pos]

	// Semántico (Burgos): retorno coherente
	// El valor de cada llamada tiene el tipo que declara la función
	mayorValor := mayorDe(totalUnidades, elemento)
	paridad := esPar(mayorValor)
	areaTri := areaTriangulo(peso, factor)
	sumaMayor := mayorValor + sumar(unidades, lotes)
	avisar(10, mayorValor)

	fmt.Println(totalUnidades, sobrante, pesoTotal, pesoMedio, negado, bonoMax, mitadPI)
	fmt.Println(etiqueta, mismoTexto, antes, pesado, fueraDeRango, elemento)
	fmt.Println(mayorValor, paridad, areaTri, sumaMayor)
	// FIN semántico
}
