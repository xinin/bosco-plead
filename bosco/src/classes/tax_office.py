class TaxOffice:
    
    users = {
        "87654321B": {  # Ana Gómez 
            "civil_status": "single",
            "genre": "W",
            "incomes": 50000,
            "dependent_children": 0
        },
        "22334455D": {  # Laura Fernández
            "civil_status": "widow",
            "genre": "W",
            "incomes": 12000,
            "dependent_children": 0
        },
        "33445566E": {  # José Ruiz
            "civil_status": "widow",
            "genre": "M",
            "incomes": 15000,
            "dependent_children": 1
        },
        "55667788G": {  # Carlos Sánchez
            "civil_status": "married",
            "genre": "M",
            "incomes": 20000,
            "dependent_children": 0
        }
    }

    @staticmethod
    def get_data(dni):
        # Buscar el usuario directamente usando el dni como clave
        return TaxOffice.users.get(dni, None)  # Devuelve None si el DNI no existe
