import calendar

ADMINISTRADOR_ID = 1
TITULO_SISTEMA = 'Control'
# Coordenadas de la empresa


# TIPO DE IDENTIFICACIONES
IDENTIFICACIONES = (
    (1, u'CÉDULA'),
    (2, u'RUC'),
    (3, u'PASAPORTE'),
    (4, u'OTRO')
)

PARENTESCOS = (
    (1, 'Padre'),
    (2, 'Madre'),
    (3, 'Abuelo'),
    (4, 'Abuela'),
    (5, 'Nieto'),
    (6, 'Nieta'),
    (7, 'Tío'),
    (8, 'Tía'),
    (9, 'Sobrino'),
    (10, 'Sobrina'),
    (11, 'Hermano'),
    (12, 'Hermana'),
    (13, 'Primo'),
    (14, 'Prima'),
    (15, 'Cuñado'),
    (16, 'Cuñada'),
    (17, 'Esposo'),
    (18, 'Esposa'),
    (19, 'Concubino'),
    (20, 'Concubina'),
    (21, 'Hijo adoptivo'),
    (22, 'Hija adoptiva'),
    (23, 'Padre adoptivo'),
    (24, 'Madre adoptiva'),
    (25, 'Suegro'),
    (26, 'Suegra'),
    (27, 'Yerno'),
    (28, 'Nuera'),
    (29, 'Cónyuge'),
    (30, 'Hermanastro'),
    (31, 'Hermanastra'),
    (32, 'Abuelo materno'),
    (33, 'Abuela materna'),
    (34, 'Abuelo paterno'),
    (35, 'Abuela paterna'),
    (36, 'Hijo biológico'),
    (37, 'Hija biológica'),
    (38, 'Hermano biológico'),
    (39, 'Hermana biológica')
)

DIAS_SEMANA = (
    (1, 'Lunes'),
    (2, 'Martes'),
    (3, 'Miércoles'),
    (4, 'Jueves'),
    (5, 'Viernes'),
    (6, 'Sábado'),
    (7, 'Domingo'),
)


def meses():
    meses_espanol = {
        1: 'Enero',
        2: 'Febrero',
        3: 'Marzo',
        4: 'Abril',
        5: 'Mayo',
        6: 'Junio',
        7: 'Julio',
        8: 'Agosto',
        9: 'Septiembre',
        10: 'Octubre',
        11: 'Noviembre',
        12: 'Diciembre'
    }

    # Obtén una lista de meses en formato "número, nombre"
    lista_meses = [{'id': numero, 'mes': nombre} for numero, nombre in meses_espanol.items()]
    return lista_meses
