
package main
import "fmt"

// Error 1: fmt.Scanln sin &
func lecturaSinDireccion() {
    var numero int
    fmt.Scanln(numero)
}

// Error 2: constante sin inicialización
func constanteSinValor() {
    const LIMITE int
}

// Error 3: paréntesis sin cerrar
func faltaCierreParentesis() {
    nuevo := (3 + 4 * 2
}

// Error 4: conector lógico incompleto
func conectorIncompleto() {
    activo := true &&
}

// Error 5: case sin :
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

// Error 6: mapa sin :
func mapaSinDosPuntos() {
    edades := map[string]int{"Ana" 20}
}
