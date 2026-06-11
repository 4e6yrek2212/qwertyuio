import pygame
import sys
import math
import random

# Настройки окна и мира
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
GRID_WIDTH = 120
GRID_HEIGHT = 45  # Сделали мир еще немного глубже
WORLD_WIDTH = GRID_WIDTH * TILE_SIZE
WORLD_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Блоки
AIR, GRASS, DIRT, STONE, TORCH = 0, 1, 2, 3, 4

TILE_COLORS = {
    GRASS: (34, 139, 34),
    DIRT: (139, 69, 19),
    STONE: (128, 128, 128),
    TORCH: (255, 165, 0)  # Оранжевый цвет для факела
}

# Цвета (RGB)
SKY_BLUE = (135, 206, 235)      # Голубое небо
PLAYER_COLOR = (255, 100, 100)  # Красный игрок

HEALTH_RED = (230, 50, 50)
HEALTH_BG = (60, 20, 20)


# Настройки темноты
DARKNESS_START_Y = 12  # С этой глубины (в блоках) начинается потемнение


class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)

    def apply(self, target_rect):
        return target_rect.move(self.rect.topleft)

    def update(self, target_rect):
        x = -target_rect.centerx + int(WIDTH / 2)
        y = -target_rect.centery + int(HEIGHT / 2)
        self.rect.x += int((x - self.rect.x) * 0.1)
        self.rect.y += int((y - self.rect.y) * 0.1)
        self.rect.x = max(-(WORLD_WIDTH - WIDTH), min(0, self.rect.x))
        self.rect.y = max(-(WORLD_HEIGHT - HEIGHT), min(0, self.rect.y))


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.font_ui = pygame.font.SysFont('Arial', 16, bold=True)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Террария: Освещение и Факелы")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False

        # Здоровье игрока
        self.max_hp = 100
        self.hp = 100
        self.time_of_day = 0.5  # Изменяется от 0.0 до 1.0
        self.day_speed = 0.0003  # Скорость смены суток


        self.world = [[AIR for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.torches = set()  # Храним координаты факелов (x, y) для быстрого расчета света

        self.generate_world()
        self.spawn_player()
        self.camera = Camera(WORLD_WIDTH, WORLD_HEIGHT)
        self.selected_block = GRASS

        # Переменные дня и ночи


    def spawn_player(self):
        start_x = GRID_WIDTH // 2
        for y in range(GRID_HEIGHT):
            if self.world[y][start_x] != AIR:
                self.player_rect = pygame.Rect(start_x * TILE_SIZE, (y - 2) * TILE_SIZE, 24, 48)
                break
        self.player_vy = 0
        self.on_ground = False
        self.game_over = False
        self.hp = self.max_hp

    def generate_world(self):
        for x in range(GRID_WIDTH):
            sine_wave = math.sin(x * 0.15) * 3
            ground_level = int(GRID_HEIGHT // 4 + sine_wave)
            ground_level = max(3, min(GRID_HEIGHT - 1, ground_level))

            for y in range(GRID_HEIGHT):
                if y == ground_level:
                    self.world[y][x] = GRASS
                elif ground_level < y < ground_level + 4:
                    self.world[y][x] = DIRT
                elif y >= ground_level + 4:
                    self.world[y][x] = STONE

        # Пещеры
        for y in range(8, GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.world[y][x] == STONE and random.random() < 0.43:
                    self.world[y][x] = AIR

        for _ in range(3):
            new_world = [row[:] for row in self.world]
            for y in range(8, GRID_HEIGHT - 1):
                for x in range(1, GRID_WIDTH - 1):
                    if self.world[y][x] in (STONE, AIR):
                        walls = sum(1 for ny in range(y - 1, y + 2) for nx in range(x - 1, x + 2) if
                                    self.world[ny][nx] == STONE)
                        if walls > 4:
                            new_world[y][x] = STONE
                        elif walls < 4:
                            new_world[y][x] = AIR
            self.world = new_world

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and not self.game_over:
                if event.key == pygame.K_1:
                    self.selected_block = GRASS
                elif event.key == pygame.K_2:
                    self.selected_block = DIRT
                elif event.key == pygame.K_3:
                    self.selected_block = STONE
                elif event.key == pygame.K_4:
                    self.selected_block = TORCH
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if self.game_over:
                    if event.button == 1 and self.respawn_button_rect.collidepoint(mx, my):
                        self.spawn_player()
                else:
                    wx, wy = mx - self.camera.rect.x, my - self.camera.rect.y
                    gx, gy = wx // TILE_SIZE, wy // TILE_SIZE

                    if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                        # --- НОВЫЙ БЛОК ОГРАНИЧЕНИЯ ДАЛЬНОСТИ ---
                        block_center_x = gx * TILE_SIZE + TILE_SIZE // 2
                        block_center_y = gy * TILE_SIZE + TILE_SIZE // 2

                        # Считаем расстояние от центра игрока до центра блока
                        distance = math.hypot(self.player_rect.centerx - block_center_x,
                                              self.player_rect.centery - block_center_y)

                        # Максимальный радиус взаимодействия в пикселях (4 блока * 32 пикселя = 128)
                        max_reach = 130

                        # Действие выполнится, только если блок в радиусе досягаемости
                        if distance <= max_reach:
                            if event.button == 1:  # Ломать блок
                                if self.world[gy][gx] == TORCH:
                                    self.torches.discard((gx, gy))
                                self.world[gy][gx] = AIR
                            elif event.button == 3:  # Ставить блок / факел
                                b_rect = pygame.Rect(gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                                if not self.player_rect.colliderect(b_rect):
                                    if self.selected_block == TORCH and self.world[gy][gx] == AIR:
                                        self.world[gy][gx] = TORCH
                                        self.torches.add((gx, gy))
                                    elif self.selected_block != TORCH:
                                        if (gx, gy) in self.torches: self.torches.discard((gx, gy))
                                        self.world[gy][gx] = self.selected_block

    def update(self):
        if self.game_over: return
        keys = pygame.key.get_pressed()
        dx = -4 if keys[pygame.K_a] or keys[pygame.K_LEFT] else (4 if keys[pygame.K_d] or keys[pygame.K_RIGHT] else 0)

        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.player_vy, self.on_ground = -10, False

        self.player_vy = min(10, self.player_vy + 0.5)
        self.player_rect.x += dx
        self.check_collisions(dx, 0)
        self.player_rect.y += self.player_vy
        self.check_collisions(0, self.player_vy)

        self.camera.update(self.player_rect)
        if self.player_rect.top > WORLD_HEIGHT: self.game_over = True

        # Урон от падения (если скорость падения была высокой в момент приземления)
        if self.on_ground and self.player_vy > 8:
            fall_damage = int((self.player_vy - 7) * 15)
            self.hp -= fall_damage
            if self.hp <= 0:
                self.hp = 0
                self.game_over = True

        # Смена дня и ночи
        self.time_of_day += self.day_speed
        if self.time_of_day > 1.0:
            self.time_of_day = 0.0

    def check_collisions(self, dx, dy):
        self.on_ground = False
        gx, gy = self.player_rect.centerx // TILE_SIZE, self.player_rect.centery // TILE_SIZE
        for y in range(max(0, gy - 3), min(GRID_HEIGHT, gy + 3)):
            for x in range(max(0, gx - 3), min(GRID_WIDTH, gx + 3)):
                # Факел не имеет коллизии (сквозь него можно ходить)
                if self.world[y][x] != AIR and self.world[y][x] != TORCH:
                    t_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.player_rect.colliderect(t_rect):
                        if dx > 0: self.player_rect.right = t_rect.left
                        if dx < 0: self.player_rect.left = t_rect.right
                        if dy > 0:
                            self.player_rect.bottom = t_rect.top
                            self.player_vy, self.on_ground = 0, True
                        if dy < 0:
                            self.player_rect.top = t_rect.bottom
                            self.player_vy = 0

    def draw_game_over_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((150, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        txt = self.font_large.render("ВЫ ПОГИБЛИ!", True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))

        self.respawn_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
        color = (180, 50, 50) if self.respawn_button_rect.collidepoint(pygame.mouse.get_pos()) else (120, 30, 30)
        pygame.draw.rect(self.screen, color, self.respawn_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.respawn_button_rect, 2, border_radius=10)

        btn = self.font_small.render("Респавн", True, (255, 255, 255))
        self.screen.blit(btn, btn.get_rect(center=self.respawn_button_rect.center))

    def draw_ui(self):
        ui_rect = pygame.Rect(15, 15, 50, 50)
        pygame.draw.rect(self.screen, (50, 50, 50), ui_rect, border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), ui_rect, 2, border_radius=5)

        # Отрисовка факела или блока в интерфейсе
        if self.selected_block == TORCH:
            pygame.draw.rect(self.screen, TILE_COLORS[TORCH], (31, 24, 18, 32))  # Делаем форму факела тоньше блока
        else:
            pygame.draw.rect(self.screen, TILE_COLORS[self.selected_block], (24, 24, 32, 32))

        self.screen.blit(self.font_ui.render("1-4: Выбор предмета (4 - Факел)", True, (255, 255, 255)), (75, 30))

    def get_sky_color(self):
        """Вычисляет текущий цвет неба в зависимости от времени суток"""
        # Синусоида дня: 0.0 - ночь, 1.0 - полдень
        day_factor = math.sin(self.time_of_day * math.pi)

        # Плавно смешиваем дневной голубой и ночной темно-синий
        r = int(135 * day_factor + 10 * (1.0 - day_factor))
        g = int(206 * day_factor + 15 * (1.0 - day_factor))
        b = int(235 * day_factor + 40 * (1.0 - day_factor))
        return (r, g, b)

    def draw_health_bar(self):
        """Рисует полоску здоровья в верхнем правом углу"""
        bar_width = 180
        bar_height = 20
        x = WIDTH - bar_width - 20
        y = 20

        # Задний фон полоски (темно-красный)
        pygame.draw.rect(self.screen, HEALTH_BG, (x, y, bar_width, bar_height), border_radius=5)
        # Текущее здоровье (яркий красный)
        current_width = int(bar_width * (self.hp / self.max_hp))
        if current_width > 0:
            pygame.draw.rect(self.screen, HEALTH_RED, (x, y, current_width, bar_height), border_radius=5)
        # Белая рамка
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2, border_radius=5)

    def get_light_level(self, x, y):
        """Вычисляет уровень темноты для конкретного блока"""
        surface_darkness = int((1.0 - math.sin(self.time_of_day * math.pi)) * 180)

        if y < DARKNESS_START_Y:
            return surface_darkness  # На поверхности всегда светло

        # Базовая темнота зависит от глубины (максимум 220 из 255 альфы)
        base_darkness = min(220, (y - DARKNESS_START_Y) * 12)

        # Ищем ближайший факел
        max_light_saved = 0
        for tx, ty in self.torches:
            dist = math.hypot(x - tx, y - ty)
            if dist < 4:  # Радиус освещения факела — 3.5 блока
                # Чем ближе к факелу, тем больше тьмы рассеивается
                light_factor = (4 - dist) / 4
                light_saved = base_darkness * light_factor
                if light_saved > max_light_saved:
                    max_light_saved = light_saved

        return max(0, int(base_darkness - max_light_saved))

    def draw(self):
        self.screen.fill(self.get_sky_color())
        sx = max(0, -self.camera.rect.x // TILE_SIZE)
        ex = min(GRID_WIDTH, sx + (WIDTH // TILE_SIZE) + 2)

        # Создаем прозрачный слой для отрисовки темноты и теней
        light_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for y in range(GRID_HEIGHT):
            for x in range(sx, ex):
                t_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                scr_rect = self.camera.apply(t_rect)

                # Рисуем блоки
                tile = self.world[y][x]
                if tile != AIR:
                    if tile == TORCH:
                        # Факел рисуем палочкой, а не целым блоком
                        torch_rect = pygame.Rect(x * TILE_SIZE + 10, y * TILE_SIZE + 6, 12, 26)
                        pygame.draw.rect(self.screen, TILE_COLORS[TORCH], self.camera.apply(torch_rect))
                    else:
                        pygame.draw.rect(self.screen, TILE_COLORS[tile], scr_rect)
                        pygame.draw.rect(self.screen, (0, 0, 0), scr_rect, 1)

                # Вычисляем и накладываем тень поверх блоков и пустот
                darkness = self.get_light_level(x, y)
                if darkness > 0:
                    pygame.draw.rect(light_layer, (0, 0, 0, darkness), scr_rect)

        # Рисуем игрока
        if not self.game_over:
            pygame.draw.rect(self.screen, PLAYER_COLOR, self.camera.apply(self.player_rect))

        # Накладываем слой темноты на экран
        self.screen.blit(light_layer, (0, 0))

        # Отрисовка интерфейса и меню смерти
        self.draw_ui()
        if self.game_over:
            self.draw_game_over_screen()

        self.draw_ui()
        self.draw_health_bar() # Отрисовка HP в углу экрана

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()

