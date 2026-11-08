package main
import "fmt"
// Errores léxicos: cadenas sin cerrar
func main() {
	saludo := "Hola Mundo
	fmt.Println(saludo)
	despedida := "Adios
}

// INICIO aporte: ANDRADE (errores sintácticos)
// Cada función contiene un error sintáctico distinto de las reglas de Andrade.

// Error 1: falta el valor a la derecha de :=
func faltaValor() {
	total :=
}

// Error 2: el if no tiene condición
func ifSinCondicion() {
	if {
		fmt.Println("mayor")
	}
}

// Error 3: falta cerrar el paréntesis de fmt.Println
func faltaParentesis() {
	fmt.Println("Hola Mundo"
}

// Error 4: falta cerrar el literal del arreglo con }
func faltaLlaveArreglo() {
	primos := [3]int{2, 3, 5
}

// Error 5: falta el valor a la derecha de = en una reasignación
func reasignacionIncompleta() {
	contador := 1
	contador =
}

// Error 6: el else está en una línea distinta a la llave de cierre del if
func elseSuelto() {
	edad := 20
	if edad > 18 {
		fmt.Println("mayor")
	}
	else {
		fmt.Println("menor")
	}
}

// Error 7: falta la llave } que cierra la función (fin de archivo inesperado)
func sinCierre() {
	contador := 1
// FIN aporte: ANDRADE (errores sintácticos)