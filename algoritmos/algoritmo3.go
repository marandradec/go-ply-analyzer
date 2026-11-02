package main

import "fmt"

func mostrarResultado(numero int, activo bool) {
	fmt.Println("Numero:", numero)
	fmt.Println("Activo:", activo)
}

func main() {
	// Constante
	const LIMITE int = 10

	// Prueba de tipos booleanos
	activo := true
	bloqueado := false

	// Operadores logicos
	permitido := activo && !bloqueado
	disponible := activo || bloqueado

	// Mapa con claves string y valores int
	edades := map[string]int{"Ana": 20, "Luis": 22}
	edades["Pedro"] = 25

	// Operadores de incremento y asignacion
	contador := 1
	contador++
	contador--
	contador += 5
	contador -= 2

	// Signo negativo y parentesis de agrupacion
	opuesto := -contador
	negativo := -(contador + 1)
	doble := (contador + 2) * 2
	ajustado := (doble - LIMITE) / (contador + 1)

	// Estructura switch
	switch contador {
	case 1:
		fmt.Println("Uno")
	case 4:
		fmt.Println("Cuatro")
	default:
		fmt.Println("Otro valor")
	}

	// Lectura de datos
	var numero int
	fmt.Println("Ingrese un numero:")
	fmt.Scanln(&numero)

	if permitido && disponible {
		mostrarResultado(numero, activo)
	}

	fmt.Println(opuesto, negativo, ajustado)
	fmt.Println(edades["Ana"])
}
