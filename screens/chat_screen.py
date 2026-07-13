import pygame

from screens.chat_list_screen import get_contact_status_text, draw_circular_profile

from ui.profile_images import load_profile_image

from settings import(
    BACKGROUND_COLOR,
    HEADER_COLOR,
    PRIMARY_COLOR,
    TEXT_COLOR,
    WIDTH,
)

MARTHA_PROFILE=None
BACK_BUTTON_RECT=pygame.Rect(15,20,60,45)

def draw_text(screen,text,font,color,x,y):
    text_surface=font.render(text,True,color)
    screen.blit(text_surface,(x,y))
def draw_chat_screen(
    screen,
    fonts,
    game_state,
    messages,
):
    global MARTHA_PROFILE

    if (
        game_state.active_chat == "Martha"
        and MARTHA_PROFILE is None
    ):
        MARTHA_PROFILE = load_profile_image(
            "martha_pp.png",
            44,
        )
    screen.fill(BACKGROUND_COLOR)
    
    pygame.draw.rect(
        screen,
        HEADER_COLOR,
        pygame.Rect(0,0,WIDTH,80,)
    )
    
    
    #back button
    draw_text(
        screen,
        "<",
        fonts["title"],
        TEXT_COLOR,
        20,
        22,
    )
    
    profile_center=(60,40)
    if game_state.active_chat=="Martha":
        draw_circular_profile(screen,
                              MARTHA_PROFILE,
                              profile_center,
                              22,)
    else:
        pygame.draw.circle(
            screen,
            (90, 90, 90),
            profile_center,
            22,
        )

        unknown_initial = fonts["normal"].render(
            "U",
            True,
            (255, 255, 255),
        )

        screen.blit(
            unknown_initial,
            unknown_initial.get_rect(center=profile_center),
        ) 
    
    #contact name
    draw_text(
        screen,
        game_state.active_chat,
        fonts["normal"],
        TEXT_COLOR,
        88,
        18,
    )
    
    #contact status
    status_text=get_contact_status_text(game_state,game_state.active_chat,)
    draw_text(
        screen,
        status_text,
        fonts["small"],
        (110, 110, 110),
        88,
        51,
    )
    
    #messages begin below the header
    y_position=115
    for message in messages[game_state.active_chat]:
        sender=message["sender"]
        text=message["text"]
        bubble_width=285
        bubble_height=65
        if sender==game_state.player_name:
            bubble_color=PRIMARY_COLOR
            message_color=(255,255,255)
            bubble_x=WIDTH-bubble_width-15
        else:
            bubble_x=15
            bubble_color=(225,225,225)
            message_color=TEXT_COLOR
        bubble_rect=pygame.Rect(
            bubble_x,
            y_position,
            bubble_width,
            bubble_height
        )
        pygame.draw.rect(
            screen,
            bubble_color,
            bubble_rect,
            border_radius=12,
        )
        draw_text(
            screen,
            text,
            fonts["small"],
            message_color,
            bubble_x+12,
            y_position+21,
        )
        y_position += bubble_height + 15
        
        if game_state.typing_contact==game_state.active_chat:
            draw_typing_bubble(screen,fonts,y_position)

def draw_typing_bubble(screen,fonts,y_position):
    bubble_width=70
    bubble_height=42
    bubble_x=15
    bubble_rect=pygame.Rect(bubble_x,y_position,bubble_width,bubble_height)
    pygame.draw.rect(screen,(225,225,225),bubble_rect,border_radius=14,)
    current_time=pygame.time.get_ticks()
    dot_count=(current_time//350)%4
    dots="."*dot_count
    if dots=="":
        dots=" "
    dot_surface=fonts["normal"].render(dots,True,(80,80,80))
    screen.blit(dot_surface,(bubble_x+23,y_position+8),)
    
def handle_chat_event(event,game_state):
    if event.type==pygame.MOUSEBUTTONDOWN:
        if BACK_BUTTON_RECT.collidepoint(event.pos):
            game_state.current_screen='chat_list'
