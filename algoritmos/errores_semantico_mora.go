package main

import "fmt"

// Asignacion estricta: var con un valor de otro tipo
func varTipoDistinto() {
	var x int = "hola"
}

// Asignacion estricta: un flotante en una variable entera
func flotanteEnEntero() {
	var y int = 3.5
}

// Asignacion estricta: constante con un valor de otro tipo
func constanteTipoDistinto() {
	const LIMITE int = "diez"
}

// Asignacion estricta: reasignacion con otro tipo
func reasignacionTipo() {
	edad := 20
	edad = "veinte"
}

// Asignacion estricta: una constante no puede modificarse
func modificarConstante() {
	const MAX int = 100
	MAX = 5
}

// Asignacion estricta: asignacion compuesta sobre una constante
func compuestaEnConstante() {
	const BASE int = 1
	BASE += 2
}

// Asignacion estricta: incremento sobre una constante
func incrementoEnConstante() {
	const N int = 1
	N++
}

// Asignacion estricta: lectura de datos sobre una constante
func lecturaEnConstante() {
	const K int = 1
	fmt.Scanln(&K)
}

func mostrar(a int, b int) {
	fmt.Println(a + b)
}

// Asignacion estricta: el argumento no coincide con el tipo del parametro
func argumentoTipoDistinto() {
	mostrar("hola", 2)
}

// Asignacion estricta: cantidad de argumentos distinta a la declarada
func cantidadDeArgumentos() {
	mostrar(1)
}

// Asignacion estricta: un elemento del arreglo de otro tipo
func literalArregloTipo() {
	notas := [3]int{1, "dos", 3}
}

// Asignacion estricta: mas elementos que el tamano del arreglo
func literalArregloExceso() {
	pares := [2]int{2, 4, 6}
}

// Asignacion estricta: un valor del mapa de otro tipo
func literalMapaTipo() {
	edades := map[string]int{"ana": "veinte"}
}

// Control con sentido logico: break fuera de un for o un switch
func breakSuelto() {
	break
}

// Control con sentido logico: break dentro de un if que no esta en un for
func breakEnIf() {
	x := 1
	if x == 1 {
		break
	}
}

// Control con sentido logico: la condicion del if no es booleana
func condicionEntera() {
	x := 5
	if x {
		fmt.Println("x")
	}
}

// Control con sentido logico: el case no tiene el tipo del switch
func caseTipoDistinto() {
	n := 1
	switch n {
	case "uno":
		fmt.Println("uno")
	default:
		fmt.Println("otro")
	}
}

// Control con sentido logico: valor repetido en dos case
func caseRepetido() {
	n := 1
	switch n {
	case 1:
		fmt.Println("uno")
	case 1:
		fmt.Println("otra vez uno")
	default:
		fmt.Println("otro")
	}
}

// Correcto: asignaciones validas, constante sin modificar y break donde corresponde
func usoValido() {
	const TOPE int = 3
	var total int = 0
	total = total + 1
	edades := map[string]int{"ana": 20}
	for i := 0; i < TOPE; i++ {
		if i == 2 {
			break
		}
		total = total + i
	}
	switch total {
	case 1:
		fmt.Println("uno")
		break
	default:
		fmt.Println("otro")
	}
	mostrar(total, TOPE)
	fmt.Println(edades["ana"])
}
