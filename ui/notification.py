import pygame

from settings import WIDTH

NOTIFICATION_HEIGHT=78

def shorten_message(message,maximum_length=42):
    if len(message)<=maximum_length:
        return message
    return message[:maximum_length-3]+"..."

def show_notification(game_state,sender,message):
    game_state.notification["visible"]=True
    game_state.notification["sender"]=sender
    game_state.notification["message"]=shorten_message(message)
    game_state.notification["shown_at"]=pygame.time.get_ticks()
    
def update_notification(game_state):
    notification=game_state.notification
    if not notification["visible"]:
        return
    current_time=pygame.time.get_ticks()
    elapsed_time=current_time-notification["shown_at"]
    
    if elapsed_time>=notification["duration"]:
        notification["visible"]=False
def draw_notification(screen, fonts, game_state):
    notification=game_state.notification
    if not notification["visible"]:
        return
    panel_rect=pygame.Rect(
        12,
        12,
        WIDTH-24,
        NOTIFICATION_HEIGHT,
    )
    
    shadow_rect=panel_rect.move(0,4)
    
    pygame.draw.rect(
        screen,
        (50,50,50),
        shadow_rect,
        border_radius=14,
    )
    
    pygame.draw.rect(
        screen,
        (255,255,255),
        panel_rect,
        border_radius=14,
    )
    
    pygame.draw.circle(
        screen,
        (65,105,225),
        (48,51),
        23,
    )
    initial_surface=fonts["normal"].render(
        notification["sender"][0],
        True,
        (255,255,255),
    )
    screen.bilt(
        initial_surface,
        initial_surface.get_rect(center=(48,51))
    )
    sender_surface=fonts["normal"].render(
        notification["sender"],
        True,
        (25,25,25),
    )
    screen.blit(sender_surface, (82, 24))

    message_surface = fonts["small"].render(
        notification["message"],
        True,
        (100, 100, 100),
    )

    screen.blit(message_surface, (82, 51))
    
def notification_was_clicked(event,game_state):
    if event.type!=pygame.MOUSEBUTTONDOWN:
        return False
    if not game_state.notification["visible"]:
        return False
    notification_rect=pygame.Rect(
        12,
        12,
        WIDTH-24,
        NOTIFICATION_HEIGHT,
    )
    return notification_rect.collidepoint(event.pos)