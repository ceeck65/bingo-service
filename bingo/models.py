from django.db import models
import uuid
import random
from typing import List, Dict, Set
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import secrets
import hashlib


class BingoCard(models.Model):
    BINGO_TYPES = [
        ('75', '75 bolas'),
        ('85', '85 bolas'),
        ('90', '90 bolas'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=100, blank=True, null=True)  # o ForeignKey si tienes usuarios
    bingo_type = models.CharField(max_length=10, choices=BINGO_TYPES)
    numbers = models.JSONField()  # lista de listas o matriz
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bingo {self.bingo_type} - {self.id}"
    
    @classmethod
    def generate_90_ball_card(cls) -> List[List]:
        """
        Genera un cartón de bingo de 90 bolas (3x9)
        Cada fila tiene exactamente 5 números y 4 espacios vacíos
        """
        max_attempts = 100
        for attempt in range(max_attempts):
            try:
                card = [[None for _ in range(9)] for _ in range(3)]
                
                # Generar números para cada fila, asegurando exactamente 5 por fila
                for row in range(3):
                    # Seleccionar 5 columnas aleatorias para esta fila
                    selected_cols = random.sample(range(9), 5)
                    
                    # Llenar las columnas seleccionadas
                    for col in selected_cols:
                        # Rango de números para esta columna
                        if col == 8:  # Última columna (80-90)
                            available_numbers = list(range(80, 91))
                        else:
                            available_numbers = list(range(col * 10 + 1, (col + 1) * 10 + 1))
                        
                        # Encontrar números no usados en esta columna
                        used_numbers = [card[r][col] for r in range(3) if card[r][col] is not None]
                        available_numbers = [num for num in available_numbers if num not in used_numbers]
                        
                        if available_numbers:
                            card[row][col] = random.choice(available_numbers)
                        else:
                            # No hay números disponibles, reintentar
                            raise ValueError("No hay números disponibles")
                
                # Verificar que cada columna tenga al menos un número
                for col in range(9):
                    col_numbers = [card[row][col] for row in range(3)]
                    if all(num is None for num in col_numbers):
                        # Esta columna está vacía, agregar un número
                        row = random.randint(0, 2)
                        if col == 8:
                            available_numbers = list(range(80, 91))
                        else:
                            available_numbers = list(range(col * 10 + 1, (col + 1) * 10 + 1))
                        
                        # Encontrar números no usados
                        used_numbers = [card[r][col] for r in range(3) if card[r][col] is not None]
                        available_numbers = [num for num in available_numbers if num not in used_numbers]
                        
                        if available_numbers:
                            card[row][col] = random.choice(available_numbers)
                        else:
                            raise ValueError("No se pudo llenar columna vacía")
                
                # Verificar que cada fila tenga exactamente 5 números
                for row in range(3):
                    non_null_count = sum(1 for num in card[row] if num is not None)
                    if non_null_count != 5:
                        raise ValueError(f"Fila {row} no tiene exactamente 5 números")
                
                return card
                
            except ValueError:
                # Reintentar si hay algún problema
                continue
        
        # Si llegamos aquí, usar un método más simple pero garantizado
        return cls._generate_simple_90_ball_card()
    
    @classmethod
    def _generate_simple_90_ball_card(cls) -> List[List]:
        """
        Método alternativo más simple para generar cartones de 90 bolas
        """
        card = [[None for _ in range(9)] for _ in range(3)]
        
        # Generar números por columna
        for col in range(9):
            # Rango de números para esta columna
            if col == 8:  # Última columna (80-90)
                numbers = list(range(80, 91))
            else:
                numbers = list(range(col * 10 + 1, (col + 1) * 10 + 1))
            
            # Seleccionar 1-3 números para esta columna
            num_count = random.randint(1, 3)
            selected_numbers = random.sample(numbers, num_count)
            
            # Colocar los números en filas aleatorias
            available_rows = list(range(3))
            random.shuffle(available_rows)
            
            for i, num in enumerate(selected_numbers):
                if i < len(available_rows):
                    row = available_rows[i]
                    card[row][col] = num
        
        # Ajustar para que cada fila tenga exactamente 5 números
        for row in range(3):
            current_numbers = [num for num in card[row] if num is not None]
            needed = 5 - len(current_numbers)
            
            if needed > 0:
                # Encontrar columnas vacías en esta fila
                empty_cols = [col for col in range(9) if card[row][col] is None]
                
                # Seleccionar columnas aleatorias para completar
                if len(empty_cols) >= needed:
                    cols_to_fill = random.sample(empty_cols, needed)
                    
                    for col in cols_to_fill:
                        # Rango de números para esta columna
                        if col == 8:
                            available_numbers = list(range(80, 91))
                        else:
                            available_numbers = list(range(col * 10 + 1, (col + 1) * 10 + 1))
                        
                        # Encontrar números no usados en esta columna
                        used_numbers = [card[r][col] for r in range(3) if card[r][col] is not None]
                        available_numbers = [num for num in available_numbers if num not in used_numbers]
                        
                        if available_numbers:
                            card[row][col] = random.choice(available_numbers)
        
        return card
    
    @classmethod
    def generate_75_ball_card(cls) -> List[List]:
        """
        Genera un cartón de bingo de 75 bolas (5x5)
        Formato clásico americano con centro libre
        """
        card = [[None for _ in range(5)] for _ in range(5)]
        
        # Definir rangos para cada columna (B-I-N-G-O)
        column_ranges = [
            (1, 16),    # B: 1-15
            (16, 31),   # I: 16-30
            (31, 46),   # N: 31-45 (centro libre)
            (46, 61),   # G: 46-60
            (61, 76),   # O: 61-75
        ]
        
        # Llenar cada columna
        for col in range(5):
            start, end = column_ranges[col]
            numbers = list(range(start, end))
            
            # Seleccionar 5 números para esta columna
            selected_numbers = random.sample(numbers, 5)
            
            # Colocar los números en la columna
            for row in range(5):
                card[row][col] = selected_numbers[row]
        
        # El centro (N, fila 2) se deja libre en bingo americano
        card[2][2] = "FREE"
        
        return card
    
    @classmethod
    def generate_85_ball_card(cls) -> List[List]:
        """
        Genera un cartón de bingo de 85 bolas (5x5)
        Formato estilo bingo americano
        """
        card = [[None for _ in range(5)] for _ in range(5)]
        
        # Definir rangos para cada columna (B-I-N-G-O)
        column_ranges = [
            (1, 17),    # B: 1-16
            (17, 33),   # I: 17-32
            (33, 49),   # N: 33-48 (centro libre)
            (49, 65),   # G: 49-64
            (65, 81),   # O: 65-80
        ]
        
        # Llenar cada columna
        for col in range(5):
            start, end = column_ranges[col]
            numbers = list(range(start, end))
            
            # Seleccionar 5 números para esta columna
            selected_numbers = random.sample(numbers, 5)
            
            # Colocar los números en la columna
            for row in range(5):
                card[row][col] = selected_numbers[row]
        
        # El centro (N, fila 2) se deja libre en bingo americano
        card[2][2] = "FREE"
        
        return card
    
    @classmethod
    def create_card(cls, bingo_type: str, user_id: str = None) -> 'BingoCard':
        """
        Crea un nuevo cartón de bingo
        """
        if bingo_type == '75':
            numbers = cls.generate_75_ball_card()
        elif bingo_type == '85':
            numbers = cls.generate_85_ball_card()
        elif bingo_type == '90':
            numbers = cls.generate_90_ball_card()
        else:
            raise ValueError(f"Tipo de bingo no válido: {bingo_type}")
        
        return cls.objects.create(
            user_id=user_id,
            bingo_type=bingo_type,
            numbers=numbers
        )
    
    def validate_card(self) -> Dict[str, any]:
        """
        Valida que el cartón cumple con las reglas del bingo
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if self.bingo_type == '90':
            # Validar cartón de 90 bolas
            if len(self.numbers) != 3:
                validation_result['errors'].append("El cartón debe tener 3 filas")
                validation_result['is_valid'] = False
            
            if len(self.numbers[0]) != 9:
                validation_result['errors'].append("El cartón debe tener 9 columnas")
                validation_result['is_valid'] = False
            
            # Verificar que cada fila tenga exactamente 5 números
            for i, row in enumerate(self.numbers):
                non_null_count = sum(1 for num in row if num is not None)
                if non_null_count != 5:
                    validation_result['errors'].append(f"La fila {i+1} debe tener exactamente 5 números")
                    validation_result['is_valid'] = False
            
            # Verificar que cada columna tenga al menos un número
            for col in range(9):
                col_numbers = [self.numbers[row][col] for row in range(3)]
                non_null_count = sum(1 for num in col_numbers if num is not None)
                if non_null_count == 0:
                    validation_result['errors'].append(f"La columna {col+1} debe tener al menos un número")
                    validation_result['is_valid'] = False
            
            # Verificar rangos de números por columna
            for col in range(9):
                col_numbers = [self.numbers[row][col] for row in range(3) if self.numbers[row][col] is not None]
                if col == 8:  # Última columna (80-90)
                    valid_range = range(80, 91)
                else:
                    valid_range = range(col * 10 + 1, (col + 1) * 10 + 1)
                
                for num in col_numbers:
                    if num not in valid_range:
                        validation_result['errors'].append(f"Número {num} fuera de rango para columna {col+1}")
                        validation_result['is_valid'] = False
            
            # Verificar números duplicados
            all_numbers = []
            for row in self.numbers:
                for num in row:
                    if num is not None:
                        all_numbers.append(num)
            
            if len(all_numbers) != len(set(all_numbers)):
                validation_result['errors'].append("Hay números duplicados en el cartón")
                validation_result['is_valid'] = False
        
        elif self.bingo_type == '75':
            # Validar cartón de 75 bolas
            if len(self.numbers) != 5:
                validation_result['errors'].append("El cartón debe tener 5 filas")
                validation_result['is_valid'] = False
            
            if len(self.numbers[0]) != 5:
                validation_result['errors'].append("El cartón debe tener 5 columnas")
                validation_result['is_valid'] = False
            
            # Verificar rangos de números por columna
            column_ranges = [
                (1, 16),    # B: 1-15
                (16, 31),   # I: 16-30
                (31, 46),   # N: 31-45
                (46, 61),   # G: 46-60
                (61, 76),   # O: 61-75
            ]
            
            for col in range(5):
                start, end = column_ranges[col]
                valid_range = range(start, end)
                
                for row in range(5):
                    num = self.numbers[row][col]
                    if num != "FREE" and num not in valid_range:
                        validation_result['errors'].append(f"Número {num} fuera de rango para columna {col+1}")
                        validation_result['is_valid'] = False
            
            # Verificar que el centro sea "FREE"
            if self.numbers[2][2] != "FREE":
                validation_result['warnings'].append("El centro del cartón debería ser 'FREE'")
        
        elif self.bingo_type == '85':
            # Validar cartón de 85 bolas
            if len(self.numbers) != 5:
                validation_result['errors'].append("El cartón debe tener 5 filas")
                validation_result['is_valid'] = False
            
            if len(self.numbers[0]) != 5:
                validation_result['errors'].append("El cartón debe tener 5 columnas")
                validation_result['is_valid'] = False
            
            # Verificar rangos de números por columna
            column_ranges = [
                (1, 17),    # B
                (17, 33),   # I
                (33, 49),   # N
                (49, 65),   # G
                (65, 81),   # O
            ]
            
            for col in range(5):
                start, end = column_ranges[col]
                valid_range = range(start, end)
                
                for row in range(5):
                    num = self.numbers[row][col]
                    if num != "FREE" and num not in valid_range:
                        validation_result['errors'].append(f"Número {num} fuera de rango para columna {col+1}")
                        validation_result['is_valid'] = False
            
            # Verificar que el centro sea "FREE"
            if self.numbers[2][2] != "FREE":
                validation_result['warnings'].append("El centro del cartón debería ser 'FREE'")
        
        return validation_result
    
    def get_display_numbers(self) -> List[List]:
        """
        Retorna los números del cartón formateados para mostrar
        """
        return self.numbers
    
    def check_winner(self, drawn_numbers: Set[int]) -> Dict[str, any]:
        """
        Verifica si el cartón es ganador con las bolas extraídas
        """
        result = {
            'is_winner': False,
            'winning_patterns': [],
            'marked_numbers': [],
            'unmarked_numbers': []
        }
        
        if self.bingo_type == '75':
            return self._check_75_ball_winner(drawn_numbers, result)
        elif self.bingo_type == '85':
            return self._check_85_ball_winner(drawn_numbers, result)
        elif self.bingo_type == '90':
            return self._check_90_ball_winner(drawn_numbers, result)
        
        return result
    
    def _check_90_ball_winner(self, drawn_numbers: Set[int], result: Dict) -> Dict:
        """Verifica patrones ganadores para bingo de 90 bolas"""
        card_numbers = set()
        marked_numbers = []
        unmarked_numbers = []
        
        # Recopilar todos los números del cartón
        for row in self.numbers:
            for num in row:
                if num is not None:
                    card_numbers.add(num)
                    if num in drawn_numbers:
                        marked_numbers.append(num)
                    else:
                        unmarked_numbers.append(num)
        
        result['marked_numbers'] = marked_numbers
        result['unmarked_numbers'] = unmarked_numbers
        
        # Verificar patrones ganadores
        patterns = []
        
        # 1. Línea horizontal (una fila completa)
        for row_idx, row in enumerate(self.numbers):
            row_numbers = [num for num in row if num is not None]
            if all(num in drawn_numbers for num in row_numbers):
                patterns.append(f"Línea horizontal (fila {row_idx + 1})")
        
        # 2. Dos líneas horizontales
        if len(patterns) >= 2:
            patterns.append("Dos líneas")
        
        # 3. Cartón completo
        if len(patterns) >= 3:
            patterns.append("Cartón completo")
        
        # 4. Línea vertical (columna completa) - menos común pero posible
        for col_idx in range(9):
            col_numbers = []
            for row in self.numbers:
                if row[col_idx] is not None:
                    col_numbers.append(row[col_idx])
            
            if len(col_numbers) >= 2 and all(num in drawn_numbers for num in col_numbers):
                patterns.append(f"Columna {col_idx + 1}")
        
        if patterns:
            result['is_winner'] = True
            result['winning_patterns'] = patterns
        
        return result
    
    def _check_75_ball_winner(self, drawn_numbers: Set[int], result: Dict) -> Dict:
        """Verifica patrones ganadores para bingo de 75 bolas"""
        marked_numbers = []
        unmarked_numbers = []
        
        # Recopilar números marcados y no marcados
        for row in self.numbers:
            for num in row:
                if num != "FREE" and num is not None:
                    if num in drawn_numbers:
                        marked_numbers.append(num)
                    else:
                        unmarked_numbers.append(num)
        
        result['marked_numbers'] = marked_numbers
        result['unmarked_numbers'] = unmarked_numbers
        
        # Verificar patrones ganadores
        patterns = []
        
        # 1. Línea horizontal
        for row_idx, row in enumerate(self.numbers):
            row_numbers = [num for num in row if num != "FREE" and num is not None]
            free_count = row.count("FREE")
            marked_in_row = sum(1 for num in row_numbers if num in drawn_numbers)
            
            if marked_in_row + free_count == 5:
                patterns.append(f"Línea horizontal (fila {row_idx + 1})")
        
        # 2. Línea vertical
        for col_idx in range(5):
            col_numbers = []
            free_count = 0
            for row in self.numbers:
                if row[col_idx] == "FREE":
                    free_count += 1
                elif row[col_idx] is not None:
                    col_numbers.append(row[col_idx])
            
            marked_in_col = sum(1 for num in col_numbers if num in drawn_numbers)
            if marked_in_col + free_count == 5:
                patterns.append(f"Columna vertical ({['B','I','N','G','O'][col_idx]})")
        
        # 3. Diagonal principal (de arriba-izquierda a abajo-derecha)
        diagonal1_numbers = []
        free_count = 0
        for i in range(5):
            if self.numbers[i][i] == "FREE":
                free_count += 1
            elif self.numbers[i][i] is not None:
                diagonal1_numbers.append(self.numbers[i][i])
        
        marked_diagonal1 = sum(1 for num in diagonal1_numbers if num in drawn_numbers)
        if marked_diagonal1 + free_count == 5:
            patterns.append("Diagonal principal")
        
        # 4. Diagonal secundaria (de arriba-derecha a abajo-izquierda)
        diagonal2_numbers = []
        free_count = 0
        for i in range(5):
            if self.numbers[i][4-i] == "FREE":
                free_count += 1
            elif self.numbers[i][4-i] is not None:
                diagonal2_numbers.append(self.numbers[i][4-i])
        
        marked_diagonal2 = sum(1 for num in diagonal2_numbers if num in drawn_numbers)
        if marked_diagonal2 + free_count == 5:
            patterns.append("Diagonal secundaria")
        
        # 5. Esquinas
        corners = []
        for i, j in [(0, 0), (0, 4), (4, 0), (4, 4)]:
            if self.numbers[i][j] == "FREE":
                corners.append("FREE")
            elif self.numbers[i][j] is not None:
                corners.append(self.numbers[i][j])
        
        marked_corners = sum(1 for corner in corners if corner == "FREE" or corner in drawn_numbers)
        if marked_corners == 4:
            patterns.append("Cuatro esquinas")
        
        # 6. Cartón completo
        total_numbers = sum(1 for row in self.numbers for num in row if num != "FREE" and num is not None)
        if len(marked_numbers) == total_numbers:
            patterns.append("Cartón completo")
        
        if patterns:
            result['is_winner'] = True
            result['winning_patterns'] = patterns
        
        return result
    
    def _check_85_ball_winner(self, drawn_numbers: Set[int], result: Dict) -> Dict:
        """Verifica patrones ganadores para bingo de 85 bolas"""
        marked_numbers = []
        unmarked_numbers = []
        
        # Recopilar números marcados y no marcados
        for row in self.numbers:
            for num in row:
                if num != "FREE" and num is not None:
                    if num in drawn_numbers:
                        marked_numbers.append(num)
                    else:
                        unmarked_numbers.append(num)
        
        result['marked_numbers'] = marked_numbers
        result['unmarked_numbers'] = unmarked_numbers
        
        # Verificar patrones ganadores
        patterns = []
        
        # 1. Línea horizontal
        for row_idx, row in enumerate(self.numbers):
            row_numbers = [num for num in row if num != "FREE" and num is not None]
            free_count = row.count("FREE")
            marked_in_row = sum(1 for num in row_numbers if num in drawn_numbers)
            
            if marked_in_row + free_count == 5:
                patterns.append(f"Línea horizontal (fila {row_idx + 1})")
        
        # 2. Línea vertical
        for col_idx in range(5):
            col_numbers = []
            free_count = 0
            for row in self.numbers:
                if row[col_idx] == "FREE":
                    free_count += 1
                elif row[col_idx] is not None:
                    col_numbers.append(row[col_idx])
            
            marked_in_col = sum(1 for num in col_numbers if num in drawn_numbers)
            if marked_in_col + free_count == 5:
                patterns.append(f"Columna vertical ({['B','I','N','G','O'][col_idx]})")
        
        # 3. Diagonal principal (de arriba-izquierda a abajo-derecha)
        diagonal1_numbers = []
        free_count = 0
        for i in range(5):
            if self.numbers[i][i] == "FREE":
                free_count += 1
            elif self.numbers[i][i] is not None:
                diagonal1_numbers.append(self.numbers[i][i])
        
        marked_diagonal1 = sum(1 for num in diagonal1_numbers if num in drawn_numbers)
        if marked_diagonal1 + free_count == 5:
            patterns.append("Diagonal principal")
        
        # 4. Diagonal secundaria (de arriba-derecha a abajo-izquierda)
        diagonal2_numbers = []
        free_count = 0
        for i in range(5):
            if self.numbers[i][4-i] == "FREE":
                free_count += 1
            elif self.numbers[i][4-i] is not None:
                diagonal2_numbers.append(self.numbers[i][4-i])
        
        marked_diagonal2 = sum(1 for num in diagonal2_numbers if num in drawn_numbers)
        if marked_diagonal2 + free_count == 5:
            patterns.append("Diagonal secundaria")
        
        # 5. Esquinas
        corners = []
        for i, j in [(0, 0), (0, 4), (4, 0), (4, 4)]:
            if self.numbers[i][j] == "FREE":
                corners.append("FREE")
            elif self.numbers[i][j] is not None:
                corners.append(self.numbers[i][j])
        
        marked_corners = sum(1 for corner in corners if corner == "FREE" or corner in drawn_numbers)
        if marked_corners == 4:
            patterns.append("Cuatro esquinas")
        
        # 6. Cartón completo
        total_numbers = sum(1 for row in self.numbers for num in row if num != "FREE" and num is not None)
        if len(marked_numbers) == total_numbers:
            patterns.append("Cartón completo")
        
        if patterns:
            result['is_winner'] = True
            result['winning_patterns'] = patterns
        
        return result


class BingoGame(models.Model):
    """Modelo para representar una partida de bingo"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_type = models.CharField(max_length=10, choices=BingoCard.BINGO_TYPES)
    name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Bingo {self.game_type} - {self.name or self.id}"
    
    def draw_ball(self) -> int:
        """Extrae una bola aleatoria según el tipo de juego"""
        if self.game_type == '75':
            return random.randint(1, 75)
        elif self.game_type == '85':
            return random.randint(1, 85)
        elif self.game_type == '90':
            return random.randint(1, 90)
        else:
            raise ValueError(f"Tipo de juego no válido: {self.game_type}")


class DrawnBall(models.Model):
    """Modelo para las bolas extraídas en una partida"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(BingoGame, on_delete=models.CASCADE, related_name='drawn_balls')
    number = models.IntegerField()
    drawn_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-drawn_at']
        unique_together = ['game', 'number']  # No se puede extraer la misma bola dos veces
    
    def __str__(self):
        return f"Bola {self.get_display_name()} - Juego {self.game.id}"
    
    def get_letter(self) -> str:
        """Obtiene la letra (B-I-N-G-O) según el número para bingo americano"""
        game_type = self.game.game_type
        
        if game_type == '75':
            # Bingo americano de 75 bolas
            if 1 <= self.number <= 15:
                return 'B'
            elif 16 <= self.number <= 30:
                return 'I'
            elif 31 <= self.number <= 45:
                return 'N'
            elif 46 <= self.number <= 60:
                return 'G'
            elif 61 <= self.number <= 75:
                return 'O'
        elif game_type == '85':
            # Bingo americano extendido de 85 bolas
            if 1 <= self.number <= 16:
                return 'B'
            elif 17 <= self.number <= 32:
                return 'I'
            elif 33 <= self.number <= 48:
                return 'N'
            elif 49 <= self.number <= 64:
                return 'G'
            elif 65 <= self.number <= 80:
                return 'O'
        elif game_type == '90':
            # Bingo europeo - no usa letras
            return ''
        
        return ''
    
    def get_display_name(self) -> str:
        """Retorna el nombre completo para mostrar (ej: B-7, I-26, G-60)"""
        letter = self.get_letter()
        if letter:
            return f"{letter}-{self.number}"
        return str(self.number)
    
    def get_color(self) -> str:
        """Retorna un color CSS según la letra para visualización"""
        colors = {
            'B': '#0066CC',  # Azul
            'I': '#FF6B35',  # Naranja
            'N': '#4CAF50',  # Verde
            'G': '#9C27B0',  # Púrpura
            'O': '#F44336',  # Rojo
        }
        letter = self.get_letter()
        return colors.get(letter, '#666666')  # Gris por defecto
    
    @classmethod
    def get_drawn_numbers(cls, game_id: str) -> Set[int]:
        """Obtiene todos los números extraídos en un juego"""
        drawn_balls = cls.objects.filter(game_id=game_id)
        return set(ball.number for ball in drawn_balls)


# === MODELOS PARA SISTEMA MULTI-TENANT ===

class Operator(models.Model):
    """Modelo para operadores/marcas del sistema whitelabel"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Nombre del operador/marca")
    code = models.CharField(
        max_length=20, 
        unique=True,
        validators=[RegexValidator(r'^[a-zA-Z0-9_-]+$', 'Solo letras, números, _ y -')],
        help_text="Código único del operador (usado en URLs)"
    )
    domain = models.CharField(max_length=100, blank=True, help_text="Dominio personalizado")
    logo_url = models.URLField(blank=True, help_text="URL del logo del operador")
    primary_color = models.CharField(max_length=7, default="#007bff", help_text="Color principal (hex)")
    secondary_color = models.CharField(max_length=7, default="#6c757d", help_text="Color secundario (hex)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Configuraciones de bingo
    allowed_bingo_types = models.JSONField(
        default=list, 
        help_text="Tipos de bingo permitidos: ['75', '85', '90']"
    )
    max_cards_per_player = models.IntegerField(default=5, help_text="Máximo cartones por jugador")
    max_cards_per_game = models.IntegerField(default=100, help_text="Máximo cartones por partida")
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_allowed_bingo_types(self):
        """Retorna los tipos de bingo permitidos para este operador"""
        return self.allowed_bingo_types or ['75', '85', '90']


class Player(models.Model):
    """Modelo para jugadores del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='players')
    
    # Información del jugador
    username = models.CharField(max_length=50, help_text="Nombre de usuario único")
    email = models.EmailField(blank=True, help_text="Email del jugador")
    phone = models.CharField(max_length=20, blank=True, help_text="Teléfono del jugador")
    
    # Información de contacto para WhatsApp/Telegram
    whatsapp_id = models.CharField(max_length=100, blank=True, help_text="ID de WhatsApp")
    telegram_id = models.CharField(max_length=100, blank=True, help_text="ID de Telegram")
    
    # Estado del jugador
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['operator', 'username']
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.operator.name})"


class BingoSession(models.Model):
    """Modelo para sesiones de bingo (partidas organizadas)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='sessions')
    
    # Información de la sesión
    name = models.CharField(max_length=100, help_text="Nombre de la sesión")
    description = models.TextField(blank=True, help_text="Descripción de la sesión")
    
    # Configuración del bingo
    bingo_type = models.CharField(max_length=10, choices=BingoCard.BINGO_TYPES)
    max_players = models.IntegerField(default=50, help_text="Máximo de jugadores")
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Costo de entrada")
    
    # *** NUEVO: Configuración de cartones ***
    total_cards = models.IntegerField(default=100, help_text="Cantidad total de cartones generados para esta sesión")
    cards_generated = models.BooleanField(default=False, help_text="Si los cartones ya fueron generados")
    allow_card_reuse = models.BooleanField(default=False, help_text="Permitir reutilizar cartones de otras sesiones")
    
    # Horarios
    scheduled_start = models.DateTimeField(help_text="Fecha y hora programada de inicio")
    actual_start = models.DateTimeField(null=True, blank=True, help_text="Fecha y hora real de inicio")
    actual_end = models.DateTimeField(null=True, blank=True, help_text="Fecha y hora real de fin")
    
    # Estado
    STATUS_CHOICES = [
        ('scheduled', 'Programada'),
        ('active', 'Activa'),
        ('paused', 'Pausada'),
        ('finished', 'Finalizada'),
        ('cancelled', 'Cancelada'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Configuraciones adicionales
    auto_start = models.BooleanField(default=False, help_text="Iniciar automáticamente")
    auto_draw_interval = models.IntegerField(default=5, help_text="Intervalo entre extracciones (segundos)")
    winning_patterns = models.JSONField(
        default=list,
        help_text="Patrones ganadores válidos para esta sesión"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, help_text="Creado por (admin/operador)")
    
    class Meta:
        ordering = ['-scheduled_start']
    
    def __str__(self):
        return f"{self.name} - {self.operator.name} ({self.bingo_type} bolas)"
    
    def get_winning_patterns(self):
        """Retorna los patrones ganadores configurados como objetos WinningPattern"""
        if not self.winning_patterns:
            # Patrones por defecto
            return WinningPattern.objects.filter(
                code__in=['horizontal_line', 'vertical_line', 'full_card'],
                is_active=True
            )
        
        # Retornar patrones configurados
        return WinningPattern.objects.filter(
            code__in=self.winning_patterns,
            is_active=True
        )
    
    def generate_cards_for_session(self):
        """Genera los cartones para esta sesión"""
        if self.cards_generated:
            return False, "Los cartones ya fueron generados para esta sesión"
        
        # Generar cartones
        cards_created = []
        for i in range(self.total_cards):
            card = BingoCardExtended.create_card(
                bingo_type=self.bingo_type,
                user_id=f"session_{self.id}_card_{i+1}"
            )
            card.session = self
            card.status = 'available'
            card.card_number = i + 1
            card.save()
            cards_created.append(card)
        
        self.cards_generated = True
        self.save()
        
        return True, f"{len(cards_created)} cartones generados exitosamente"
    
    def get_available_cards(self):
        """Retorna los cartones disponibles para esta sesión"""
        return self.cards.filter(status='available')
    
    def get_reserved_cards(self):
        """Retorna los cartones reservados pero no vendidos"""
        return self.cards.filter(status='reserved')
    
    def get_sold_cards(self):
        """Retorna los cartones vendidos"""
        return self.cards.filter(status='sold')


class PlayerSession(models.Model):
    """Modelo para relacionar jugadores con sesiones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(BingoSession, on_delete=models.CASCADE, related_name='player_sessions')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='session_participations')
    
    # Estado de participación
    joined_at = models.DateTimeField(auto_now_add=True)
    cards_count = models.IntegerField(default=0, help_text="Número de cartones del jugador")
    is_active = models.BooleanField(default=True)
    
    # Resultados
    has_won = models.BooleanField(default=False)
    winning_cards = models.JSONField(default=list, help_text="IDs de cartones ganadores")
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monto del premio")
    
    class Meta:
        unique_together = ['session', 'player']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.player.username} en {self.session.name}"


class BingoCardExtended(BingoCard):
    """Extensión del modelo BingoCard para el sistema multi-tenant"""
    session = models.ForeignKey(BingoSession, on_delete=models.CASCADE, related_name='cards', null=True, blank=True)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, related_name='cards', null=True, blank=True)
    
    # *** NUEVO: Estado y número de cartón ***
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('reserved', 'Reservado'),
        ('sold', 'Vendido'),
        ('cancelled', 'Cancelado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', help_text="Estado del cartón")
    card_number = models.IntegerField(default=0, help_text="Número del cartón en la sesión")
    
    # Información adicional
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Precio de compra")
    is_winner = models.BooleanField(default=False, help_text="Es cartón ganador")
    winning_patterns = models.JSONField(default=list, help_text="Patrones ganadores")
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monto del premio")
    
    # *** NUEVO: Timestamps de selección ***
    reserved_at = models.DateTimeField(null=True, blank=True, help_text="Fecha de reserva")
    purchased_at = models.DateTimeField(null=True, blank=True, help_text="Fecha de compra")
    
    class Meta:
        ordering = ['session', 'card_number']
        unique_together = ['session', 'card_number']
    
    def __str__(self):
        return f"Cartón #{self.card_number} - {self.bingo_type} ({self.get_status_display()})"
    
    def reserve_for_player(self, player):
        """Reserva el cartón para un jugador"""
        if self.status != 'available':
            return False, f"El cartón no está disponible (estado: {self.get_status_display()})"
        
        from django.utils import timezone
        self.player = player
        self.status = 'reserved'
        self.reserved_at = timezone.now()
        self.save()
        
        return True, "Cartón reservado exitosamente"
    
    def mark_as_sold(self):
        """Marca el cartón como vendido"""
        if self.status != 'reserved':
            return False, f"El cartón debe estar reservado primero (estado actual: {self.get_status_display()})"
        
        from django.utils import timezone
        self.status = 'sold'
        self.purchased_at = timezone.now()
        self.purchase_price = self.session.entry_fee if self.session else 0
        self.save()
        
        return True, "Cartón vendido exitosamente"
    
    def release(self):
        """Libera el cartón para que esté disponible nuevamente"""
        if self.status in ['sold', 'cancelled']:
            return False, f"No se puede liberar un cartón {self.get_status_display()}"
        
        self.player = None
        self.status = 'available'
        self.reserved_at = None
        self.save()
        
        return True, "Cartón liberado exitosamente"
    
    def can_be_reused_in_session(self, new_session):
        """Verifica si el cartón puede ser reutilizado en otra sesión"""
        if self.bingo_type != new_session.bingo_type:
            return False, "El tipo de bingo no coincide"
        
        if not new_session.allow_card_reuse:
            return False, "La sesión no permite reutilizar cartones"
        
        return True, "El cartón puede ser reutilizado"
    
    def check_card_validity(self):
        """Valida el cartón usando el método de la clase padre"""
        # Llamar al método de la instancia padre usando super()
        # Pero primero necesitamos acceder al objeto BingoCard subyacente
        # Como BingoCardExtended hereda de BingoCard, los métodos deberían estar disponibles
        # El problema es que los métodos no son @classmethod sino de instancia
        
        # Solución: implementar el método directamente aquí
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if self.bingo_type == '90':
            # Validar cartón de 90 bolas
            if len(self.numbers) != 3:
                validation_result['errors'].append("El cartón debe tener 3 filas")
                validation_result['is_valid'] = False
            
            if self.numbers and len(self.numbers[0]) != 9:
                validation_result['errors'].append("El cartón debe tener 9 columnas")
                validation_result['is_valid'] = False
        
        elif self.bingo_type in ['75', '85']:
            # Validar cartón de 75/85 bolas
            if len(self.numbers) != 5:
                validation_result['errors'].append("El cartón debe tener 5 filas")
                validation_result['is_valid'] = False
            
            if self.numbers and len(self.numbers[0]) != 5:
                validation_result['errors'].append("El cartón debe tener 5 columnas")
                validation_result['is_valid'] = False
        
        return validation_result


class BingoGameExtended(BingoGame):
    """Extensión del modelo BingoGame para el sistema multi-tenant"""
    session = models.ForeignKey(BingoSession, on_delete=models.CASCADE, related_name='games', null=True, blank=True)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='games', null=True, blank=True)
    
    # Configuraciones adicionales
    auto_draw = models.BooleanField(default=False, help_text="Extracción automática")
    draw_interval = models.IntegerField(default=5, help_text="Intervalo entre extracciones (segundos)")
    max_balls = models.IntegerField(default=0, help_text="Máximo de bolas a extraer (0 = sin límite)")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Partida {self.game_type} - {self.operator.name if self.operator else 'Sin operador'}"


# === SISTEMA DE AUTENTICACIÓN ===

class APIKey(models.Model):
    """Modelo para API Keys de autenticación"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='api_keys')
    
    # Credenciales
    name = models.CharField(max_length=100, help_text="Nombre descriptivo del API Key")
    key = models.CharField(max_length=64, unique=True, help_text="API Key pública")
    secret_hash = models.CharField(max_length=128, help_text="Hash del secret")
    
    # Permisos
    PERMISSION_CHOICES = [
        ('read', 'Solo lectura'),
        ('write', 'Lectura y escritura'),
        ('admin', 'Administrador'),
    ]
    permission_level = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='write')
    
    # Configuraciones
    is_active = models.BooleanField(default=True)
    allowed_ips = models.JSONField(default=list, blank=True, help_text="IPs permitidas (vacío = todas)")
    rate_limit = models.IntegerField(default=100, help_text="Requests por minuto")
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Fecha de expiración")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.operator.name}) - {self.key[:8]}..."
    
    @classmethod
    def generate_credentials(cls):
        """Genera un par de key y secret"""
        key = secrets.token_urlsafe(32)  # API Key pública
        secret = secrets.token_urlsafe(48)  # Secret privado
        return key, secret
    
    @classmethod
    def hash_secret(cls, secret: str) -> str:
        """Crea hash del secret para almacenar"""
        return hashlib.sha256(secret.encode()).hexdigest()
    
    def verify_secret(self, secret: str) -> bool:
        """Verifica que el secret coincida con el hash almacenado"""
        secret_hash = self.hash_secret(secret)
        return secrets.compare_digest(self.secret_hash, secret_hash)
    
    def update_last_used(self):
        """Actualiza la última vez que se usó la API Key"""
        from django.utils import timezone
        self.last_used = timezone.now()
        self.save(update_fields=['last_used'])
    
    def is_valid(self) -> tuple:
        """Verifica si la API Key es válida"""
        if not self.is_active:
            return False, "API Key inactiva"
        
        if self.expires_at:
            from django.utils import timezone
            if timezone.now() > self.expires_at:
                return False, "API Key expirada"
        
        return True, "API Key válida"


# === SISTEMA DE PATRONES DE VICTORIA ===

class WinningPattern(models.Model):
    """Patrones de victoria configurables para el bingo"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='winning_patterns', null=True, blank=True)
    
    # Información básica
    name = models.CharField(max_length=100, help_text="Nombre del patrón (ej: Línea Horizontal)")
    code = models.CharField(max_length=50, unique=True, help_text="Código único del patrón")
    description = models.TextField(blank=True, help_text="Descripción del patrón")
    
    # Categoría
    CATEGORY_CHOICES = [
        ('classic', 'Clásico'),
        ('special', 'Especial'),
        ('custom', 'Personalizado'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='classic')
    
    # Tipo de bingo compatible
    COMPATIBLE_TYPES = [
        ('all', 'Todos'),
        ('75', 'Solo 75 bolas'),
        ('85', 'Solo 85 bolas'),
        ('90', 'Solo 90 bolas'),
    ]
    compatible_with = models.CharField(max_length=10, choices=COMPATIBLE_TYPES, default='all')
    
    # Configuración del patrón
    pattern_type = models.CharField(max_length=50, help_text="Tipo: horizontal_line, vertical_line, diagonal, full_card, etc.")
    pattern_data = models.JSONField(default=dict, blank=True, help_text="Datos adicionales del patrón (posiciones, etc.)")
    
    # Premio
    prize_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, help_text="Multiplicador del premio")
    
    # Jackpot progresivo
    has_jackpot = models.BooleanField(default=False, help_text="¿Tiene jackpot progresivo?")
    jackpot_max_balls = models.IntegerField(null=True, blank=True, help_text="Máximo de bolas para ganar jackpot")
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False, help_text="Patrón del sistema (no se puede eliminar)")
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Patrón de Victoria'
        verbose_name_plural = 'Patrones de Victoria'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    @classmethod
    def create_system_patterns(cls):
        """Crea los patrones del sistema si no existen"""
        patterns = [
            # Patrones Clásicos
            {
                'code': 'horizontal_line',
                'name': 'Línea Horizontal',
                'description': 'Completa una fila horizontal de números',
                'category': 'classic',
                'pattern_type': 'horizontal_line',
                'compatible_with': 'all',
                'is_system': True,
            },
            {
                'code': 'vertical_line',
                'name': 'Línea Vertical',
                'description': 'Completa una columna vertical',
                'category': 'classic',
                'pattern_type': 'vertical_line',
                'compatible_with': 'all',
                'is_system': True,
            },
            {
                'code': 'diagonal_line',
                'name': 'Línea Diagonal',
                'description': 'Completa una diagonal desde esquina a esquina',
                'category': 'classic',
                'pattern_type': 'diagonal_line',
                'compatible_with': '75',  # Solo para 75 bolas (5x5)
                'is_system': True,
            },
            {
                'code': 'full_card',
                'name': 'Cartón Lleno (Bingo)',
                'description': 'Marca todos los números del cartón',
                'category': 'classic',
                'pattern_type': 'full_card',
                'compatible_with': 'all',
                'prize_multiplier': 2.0,
                'is_system': True,
            },
            # Patrones Especiales
            {
                'code': 'four_corners',
                'name': 'Cuatro Esquinas',
                'description': 'Marca las cuatro esquinas del cartón',
                'category': 'special',
                'pattern_type': 'four_corners',
                'compatible_with': '75',
                'is_system': True,
            },
            {
                'code': 'x_pattern',
                'name': 'X o Cruz',
                'description': 'Forma una X con las dos diagonales',
                'category': 'special',
                'pattern_type': 'x_pattern',
                'compatible_with': '75',
                'prize_multiplier': 1.5,
                'is_system': True,
            },
            {
                'code': 'letter_l',
                'name': 'Letra L',
                'description': 'Forma una L en el cartón',
                'category': 'special',
                'pattern_type': 'letter_l',
                'compatible_with': '75',
                'is_system': True,
            },
            {
                'code': 'letter_t',
                'name': 'Letra T',
                'description': 'Forma una T en el cartón',
                'category': 'special',
                'pattern_type': 'letter_t',
                'compatible_with': '75',
                'is_system': True,
            },
            {
                'code': 'blackout_jackpot',
                'name': 'Jackpot Rápido',
                'description': 'Bingo completo en menos de 50 bolas',
                'category': 'special',
                'pattern_type': 'full_card',
                'compatible_with': '75',
                'has_jackpot': True,
                'jackpot_max_balls': 50,
                'prize_multiplier': 5.0,
                'is_system': True,
            },
        ]
        
        created_count = 0
        for pattern_data in patterns:
            pattern, created = cls.objects.get_or_create(
                code=pattern_data['code'],
                defaults=pattern_data
            )
            if created:
                created_count += 1
        
        return created_count
    
    def check_pattern(self, marked_numbers: List[int], card_numbers: List[List[int]], bingo_type: str, balls_drawn: int = 0) -> dict:
        """
        Verifica si el patrón se cumple con los números marcados
        
        Args:
            marked_numbers: Lista de números marcados
            card_numbers: Matriz del cartón
            bingo_type: Tipo de bingo (75, 85, 90)
            balls_drawn: Cantidad de bolas extraídas
        
        Returns:
            dict con 'is_winner', 'pattern_name', 'prize_multiplier', 'is_jackpot'
        """
        # Verificar compatibilidad
        if self.compatible_with not in ['all', bingo_type]:
            return {'is_winner': False, 'reason': 'Patrón no compatible con este tipo de bingo'}
        
        # Verificar jackpot
        is_jackpot = False
        if self.has_jackpot and self.jackpot_max_balls and balls_drawn > 0:
            is_jackpot = balls_drawn <= self.jackpot_max_balls
        
        # Delegar según el tipo de patrón
        if self.pattern_type == 'horizontal_line':
            is_winner = self._check_horizontal_line(marked_numbers, card_numbers)
        elif self.pattern_type == 'vertical_line':
            is_winner = self._check_vertical_line(marked_numbers, card_numbers)
        elif self.pattern_type == 'diagonal_line':
            is_winner = self._check_diagonal_line(marked_numbers, card_numbers)
        elif self.pattern_type == 'full_card':
            is_winner = self._check_full_card(marked_numbers, card_numbers)
        elif self.pattern_type == 'four_corners':
            is_winner = self._check_four_corners(marked_numbers, card_numbers)
        elif self.pattern_type == 'x_pattern':
            is_winner = self._check_x_pattern(marked_numbers, card_numbers)
        elif self.pattern_type == 'letter_l':
            is_winner = self._check_letter_l(marked_numbers, card_numbers)
        elif self.pattern_type == 'letter_t':
            is_winner = self._check_letter_t(marked_numbers, card_numbers)
        else:
            is_winner = False
        
        return {
            'is_winner': is_winner,
            'pattern_name': self.name,
            'pattern_code': self.code,
            'prize_multiplier': float(self.prize_multiplier) * (2.0 if is_jackpot else 1.0),
            'is_jackpot': is_jackpot,
            'balls_drawn': balls_drawn
        }
    
    def _check_horizontal_line(self, marked: List[int], card: List[List[int]]) -> bool:
        """Verifica línea horizontal"""
        for row in card:
            non_zero = [num for num in row if num != 0]
            if all(num in marked for num in non_zero):
                return True
        return False
    
    def _check_vertical_line(self, marked: List[int], card: List[List[int]]) -> bool:
        """Verifica línea vertical"""
        cols = len(card[0])
        for col in range(cols):
            column_numbers = [card[row][col] for row in range(len(card)) if card[row][col] != 0]
            if column_numbers and all(num in marked for num in column_numbers):
                return True
        return False
    
    def _check_diagonal_line(self, marked: List[int], card: List[List[int]]) -> bool:
        """Verifica línea diagonal (solo para 5x5)"""
        if len(card) != 5 or len(card[0]) != 5:
            return False
        
        # Diagonal principal (top-left a bottom-right)
        diagonal1 = [card[i][i] for i in range(5) if card[i][i] != 0]
        if diagonal1 and all(num in marked for num in diagonal1):
            return True
        
        # Diagonal inversa (top-right a bottom-left)
        diagonal2 = [card[i][4-i] for i in range(5) if card[i][4-i] != 0]
        if diagonal2 and all(num in marked for num in diagonal2):
            return True
        
        return False
    
    def _check_full_card(self, marked: List[int], card: List[List[int]]) -> bool:
        """Verifica cartón lleno"""
        all_numbers = []
        for row in card:
            all_numbers.extend([num for num in row if num != 0])
        return all(num in marked for num in all_numbers)
    
    def _check_four_corners(self, marked: List[int], card: List[List[int]]) -> bool:
        """Verifica cuatro esquinas (solo para 5x5)"""
        if len(card) != 5 or len(card[0]) != 5:
            return False
        
        corners = [
            card[0][0],   # Top-left
            card[0][4],   # Top-right
            card[4][0],   # Bottom-left
            card[4][4]    # Bottom-right
        ]
        corners = [c for c in corners if c != 0]
        return all(num in marked for num in corners)
    
    def _check_x_pattern(self, marked: List[int], card: List[List[int]]) -> bool:
        """Verifica patrón X (ambas diagonales)"""
        if len(card) != 5 or len(card[0]) != 5:
            return False
        
        # Diagonal principal
        diagonal1 = [card[i][i] for i in range(5) if card[i][i] != 0]
        # Diagonal inversa
        diagonal2 = [card[i][4-i] for i in range(5) if card[i][4-i] != 0]
        
        all_diagonal = diagonal1 + diagonal2
        return all(num in marked for num in all_diagonal)
    
    def _check_letter_l(self, marked: List[int], card: List[List[int]]) -> bool:
        """Verifica patrón L (primera columna + última fila)"""
        if len(card) != 5 or len(card[0]) != 5:
            return False
        
        # Primera columna
        first_col = [card[row][0] for row in range(5) if card[row][0] != 0]
        # Última fila
        last_row = [card[4][col] for col in range(5) if card[4][col] != 0]
        
        l_pattern = first_col + last_row
        return all(num in marked for num in l_pattern)
    
    def _check_letter_t(self, marked: List[int], card: List[List[int]]) -> bool:
        """Verifica patrón T (primera fila + columna central)"""
        if len(card) != 5 or len(card[0]) != 5:
            return False
        
        # Primera fila
        first_row = [card[0][col] for col in range(5) if card[0][col] != 0]
        # Columna central
        middle_col = [card[row][2] for row in range(5) if card[row][2] != 0]
        
        t_pattern = first_row + middle_col
        return all(num in marked for num in t_pattern)