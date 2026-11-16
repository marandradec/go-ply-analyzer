package main

import "fmt"

func mostrarResultado(numero int, activo bool) {
	fmt.Println("Numero:", numero)
	fmt.Println("Activo:", activo)
}

// INICIO aporte: MORA (semántico, función)
// Cada argumento de la llamada debe tener el tipo del parámetro correspondiente
func describir(nombre string, cupos int, vigente bool) {
	fmt.Println(nombre, cupos, vigente)
}
// FIN aporte: MORA (semántico, función)

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
	// INICIO aporte: MORA (sintáctico)
	// switch con break, conectores combinados con comparaciones y
	switch contador {
	case 1:
		fmt.Println("Uno")
		break
	case 2:
		fmt.Println("Dos")
	default:
		fmt.Println("Otro")
	}
	// asignación compuesta e incremento sobre un elemento de mapa
	valido := contador >= 18 && !bloqueado
	coincide := contador == 2 || contador != 4
	edades["Luis"] += 1
	edades["Luis"]++
	fmt.Println(valido, coincide)
	// FIN aporte: MORA (sintáctico)

	fmt.Println(opuesto, negativo, ajustado)
	fmt.Println(edades["Ana"])

	// INICIO aporte: MORA (semántico)
	// Asignación estricta: cada valor tiene el tipo declarado de su variable.
	// Las constantes solo se leen, nunca se modifican
	const ETIQUETA string = "Nivel"
	const ESTRICTO bool = true
	var intentos int = 3
	var nota float64 = 8.5
	var mensaje string = ETIQUETA
	var habilitado bool = ESTRICTO
	var cupo int
	cupo = intentos + LIMITE
	nota = nota * 1.5
	mensaje = mensaje + " alto"
	habilitado = cupo > intentos

	// Arreglos, mapas y literales con elementos del tipo declarado
	var notas [3]int
	notas[0] = intentos
	var pesos [2]float64
	pesos[1] = nota
	resumen := [3]string{"alto", "medio", "bajo"}
	precios := map[string]float64{"pan": 0.5, "leche": 1.25}
	precios["queso"] = 3.75
	inventario := map[string]int{"pan": 10}
	inventario["pan"] += 5
	fmt.Println(notas[0], pesos[1], resumen[2], precios["queso"], inventario["pan"])

	// Los argumentos de la llamada coinciden con los parámetros (string, int, bool)
	describir(ETIQUETA, cupo, habilitado)

	// Control con sentido lógico: break solo dentro de un for o un switch
	// y las condiciones de if y for son booleanas
	for intento := 1; intento <= 5; intento++ {
		if intento == intentos {
			break
		}
		fmt.Println("Intento", intento)
	}

	var saldo int = 20
	for saldo > 0 {
		saldo -= 7
		if saldo < 5 {
			break
		}
	}
	fmt.Println("Saldo", saldo)

	// switch dentro de un for, con break y con case del mismo tipo que la expresión
	for ronda := 1; ronda <= 3; ronda++ {
		switch ronda {
		case 1:
			fmt.Println("Primera ronda")
		case 2:
			fmt.Println("Segunda ronda")
			break
		default:
			fmt.Println("Ultima ronda")
		}
	}

	switch mensaje {
	case "Nivel alto":
		fmt.Println("Nivel alto")
	case "Nivel bajo":
		fmt.Println("Nivel bajo")
		break
	}

	if habilitado && cupo > 0 {
		fmt.Println("Con cupo")
	} else {
		fmt.Println("Sin cupo")
	}
	// FIN aporte: MORA (semántico)
}
