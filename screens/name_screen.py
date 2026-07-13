import pygame

from settings import(
    BACKGROUND_COLOR,
    BORDER_COLOR,
    INPUT_COLOR,
    PRIMARY_COLOR,
    SECONDARY_TEXT_COLOR,
    TEXT_COLOR,
)

NAME_INPUT_RECT=pygame.Rect(45,330,300,55)
CONTINUE_BUTTON_RECT=pygame.Rect(95,415,200,55)

def draw_text(screen,text,font,color,x,y):
    text_surface=font.render(text,True,color)
    screen.blit(text_surface,(x,y))
    
def draw_name_screen(screen,fonts,game_state):
    screen.fill(BACKGROUND_COLOR)
    draw_text(
        screen,
        "What is your name?",
        fonts["title"],
        TEXT_COLOR,
        65,
        220,
    )
    pygame.draw.rect(
        screen,
        INPUT_COLOR,
        NAME_INPUT_RECT,
        border_radius=8,
    )
    
    border_color = (
        PRIMARY_COLOR
        if game_state.name_input_active
        else BORDER_COLOR
    )

    border_width = 3 if game_state.name_input_active else 2

    pygame.draw.rect(
        screen,
        border_color,
        NAME_INPUT_RECT,
        width=border_width,
        border_radius=8,
    )
    if game_state.player_name:
        displayed_text=game_state.player_name
        displayed_color=TEXT_COLOR
    elif game_state.name_input_active:
        displayed_text=""
        displayed_color=TEXT_COLOR
    else:
        displayed_text="Enter your name"
        displayed_color=SECONDARY_TEXT_COLOR
    text_x = NAME_INPUT_RECT.x + 15
    text_y = NAME_INPUT_RECT.y + 14

    draw_text(
        screen,
        displayed_text,
        fonts["normal"],
        displayed_color,
        text_x,
        text_y
    )
    
    if game_state.name_input_active:
        cursor_visible=(pygame.time.get_ticks()//500)%2==0
        if cursor_visible:
            typed_width=fonts["normal"].size(game_state.player_name)[0]
            cursor_x=text_x+typed_width+2
            pygame.draw.line(screen,
                             TEXT_COLOR,
                             (cursor_x,text_y+2),
                             (cursor_x,text_y+25),
                             2,)
    button_color=(
        PRIMARY_COLOR
        if game_state.player_name.strip()
        else BORDER_COLOR
    )
    
    pygame.draw.rect(
        screen,
        button_color,
        CONTINUE_BUTTON_RECT,
        border_radius=10,
    )
    
    draw_text(
        screen,
        "Continue",
        fonts["normal"],
        (255,255,255),
        CONTINUE_BUTTON_RECT.x+55,
        CONTINUE_BUTTON_RECT.y+14,
    )
    
def handle_name_screen_events(event,game_state):
    if event.type==pygame.KEYDOWN:
        print("Key pressed:", event.key)
        if not game_state.name_input_active:
            return
        if event.key==pygame.K_BACKSPACE:
            game_state.player_name=game_state.player_name[:-1]
        elif event.key==pygame.K_RETURN:
            confirm_name(game_state)
        elif(
            event.unicode.isprintable()
            and len(game_state.player_name)<16
        ):
            game_state.player_name+=event.unicode
    elif event.type==pygame.MOUSEBUTTONDOWN:
        print("Mouse click detected:", event.pos)
        if NAME_INPUT_RECT.collidepoint(event.pos):
            print("NAME INPUT SELECTED")
            game_state.name_input_active=True
        else:
            game_state.name_input_active=False
        if CONTINUE_BUTTON_RECT.collidepoint(event.pos):
            print("CONTINUE CLICKED")
            confirm_name(game_state)
def confirm_name(game_state):
    cleaned_name=game_state.player_name.strip()
    if cleaned_name:
        game_state.player_name=cleaned_name
        game_state.intro_scene_index=0
        game_state.intro_phase="background_fade_in"
        game_state.intro_alpha=0
        game_state.current_screen="intro"