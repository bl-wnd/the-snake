import sys
from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
O_POINT = (0, 0)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Родительский класс игровых объектов."""

    def __init__(
        self, position=SCREEN_CENTER,
        body_color=BOARD_BACKGROUND_COLOR
    ):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Метод заглушка. Нужен для реализации полиморфизма."""
        raise NotImplementedError(
            f'Необходимо переопределить метод draw() '
            f'в дочернем классе {self.__class__.__name__}.'
        )


class Apple(GameObject):
    """Класс описывающий яблоко.

    Содержит информацию о позиции, цвете,
    а также методы генерации позиции и отрисовки.
    """

    def __init__(self, position=O_POINT, body_color=APPLE_COLOR):
        super().__init__(position, body_color)

    def randomize_position(self, occupied_cells):
        """Метод рандомной генерации положения яблока
        Учитывает позицию змейки на игровом поле и
        не генерирует яблоко на теле змейки.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_cells:
                break

    def draw(self):
        """Метод отрисовки яблока"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс описывающий змейку и ёё поведение.

    Описывает действия змейки: движение, изменение направления,
    отрисовка змейки и сброс игры при столкновении.
    """

    def __init__(self, position=SCREEN_CENTER, body_color=SNAKE_COLOR):
        super().__init__(position, body_color)
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        # Не стал вызывать reset, т.к. в начале игры змейка должна двигаться
        # вправо, а после столкновения рандомное направление

    def get_head_position(self):
        """Метод определения координат головы змеи."""
        return self.positions[0]

    def move(self):
        """Метод движения змеи.
        Добавляет новые координаты головы, стирает лишний хвост.
        """
        head = self.get_head_position()
        # Высчитываем новые координаты головы и берём остаток от деления
        # на ширину/высоту экрана, чтобы проходить сквозь границы
        new_head_x = (head[0] + GRID_SIZE * self.direction[0]) % SCREEN_WIDTH
        new_head_y = (head[1] + GRID_SIZE * self.direction[1]) % SCREEN_HEIGHT
        new_head = (new_head_x, new_head_y)
        self.positions.insert(0, new_head)
        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку"""
        # Насколько я понял, next_direction нужен для отделения
        # пользовательского ввода от логики. Оставил так
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Метод отрисовки змеи."""
        rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Метод сброса игры.
        Исользуется когда голова змеи сталкивается с телом.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Функция основного игрового цикла."""
    pygame.init()
    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        # Насколько я понял, next_direction нужен для отделения
        # пользовательского ввода от логики. Оставил так
        snake.update_direction()
        snake.move()
        # Обработка съедания яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        # Обработка столкновения головы змейки с телом
        elif snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
