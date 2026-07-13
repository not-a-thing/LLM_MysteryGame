import pygame


WIDTH = 390
HEIGHT = 780
FPS = 60

BACKGROUND_COLOR = (245, 245, 245)
HEADER_COLOR = (255, 255, 255)
INPUT_COLOR = (255, 255, 255)

PRIMARY_COLOR = (65, 105, 225)
TEXT_COLOR = (30, 30, 30)
SECONDARY_TEXT_COLOR = (110, 110, 110)
BORDER_COLOR = (210, 210, 210)
UNREAD_COLOR = (210, 55, 55)


def create_fonts() -> dict[str, pygame.font.Font]:
    return {
        "title": pygame.font.Font(None, 38),
        "normal": pygame.font.Font(None, 28),
        "small": pygame.font.Font(None, 22),
    }