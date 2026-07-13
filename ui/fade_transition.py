import pygame
from settings import HEIGHT,WIDTH

FADE_SPEED=4

def update_chapter_transition(game_state):
    if not game_state.chapter_transition_active:
        return
    game_state.chapter_transition_alpha+=FADE_SPEED
    if game_state.chapter_transition_alpha>=255:
        game_state.chapter_transition_alpha=255
        
        #Later will load next chapter
        print("Transition complete: ", game_state.chapter_transition_target)
        
def draw_chapter_transition(screen, game_state):
    if not game_state.chapter_transition_active:
        return
    overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    overlay.fill((0,0,0,game_state.chapter_transition_alpha))
    
    screen.blit(overlay,(0,0))