package main
import "fmt"
//Errores léxicos: Errores voluntarios
func main() {
    valor := 10
    valor @ 5
    valor # 6
    valor $ 7
    fmt.Println(valor)
}
// Errores sintácticos:
// Cada función contiene un error sintáctico distinto de las reglas de Mora.

// Error 1: fmt.Scanln necesita & antes de la variable
func lecturaSinDireccion() {
	var numero int
	fmt.Scanln(numero)
}

// Error 2: la constante debe inicializarse
func constanteSinValor() {
	const LIMITE int
}

// Error 3: falta cerrar el paréntesis
func faltaCierreParentesis() {
	nuevo := (3 + 4 * 2
}

// Error 4: falta el operando después de &&
func conectorIncompleto() {
	activo := true &&
}

// Error 5: falta : después del valor del case
func casoSinDosPuntos() {
	dia := 2
	switch dia {
	case 1
		fmt.Println("lunes")
	case 2:
		fmt.Println("martes")
	default:
		fmt.Println("otro")
	}
}

// Error 6: falta : entre la clave y el valor del mapa
func mapaSinDosPuntos() {
	edades := map[string]int{"Ana" 20}
}
