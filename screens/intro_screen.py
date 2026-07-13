from pathlib import Path

import pygame

from settings import(
    HEIGHT,
    PRIMARY_COLOR,
    TEXT_COLOR,
    WIDTH,
)

INTRO_SCENES=[
    ("You are a student at Alhambra University."
    ),
    (
    "For the past two years, Sarah and Martha have been "
    "your closest friends."
    ),
    (
        "Late last night, Sarah was found unconcious inside "
        "an empty classroom."
    ),
    (
        "She had suffered a serious head injury beside a "
        "damaged desk."
    ),
    (
        "By the time help arrived, Sarah was believed to be dead."
    ),
    (
        "The police have not explained what happened, and no "
        "witnesses have come forward."
    ),
    (
        "Still in shock, you open your phone."
    ),
    (
        "You decide to contact your best friend, Martha."
    ),
]
BACKGROUND_IMAGE=None
FADE_SPEED=4
TEXT_MAX_ALPHA=255
BACKGROUND_MAX_ALPHA=255

CONTINUE_RECT=pygame.Rect(85,HEIGHT-90,220,45)

CONTINUE_BUTTON_RECT=pygame.Rect(95,690,200,55)

#IMAGE LOADING
def load_background():
    image_path=(Path(__file__).resolve().parent.parent
    /"assets"
    /"images"
    /"university.png"
    )
    try:
        image=pygame.image.load(str(image_path)).convert()
        return pygame.transform.smoothscale(image,(WIDTH,HEIGHT))
    except (pygame.error,FileNotFoundError) as e:
        print(f"Error loading background image: {e}")
        return None
    
#TEXT HELPERS
def wrap_text(text,font,max_width):
    words=text.split(" ")
    lines=[]
    current_line=""
    
    for word in words:
        test_line=f"{current_line} {word}".strip()
        
        if font.size(test_line)[0] <= max_width:
            current_line=test_line
        else:
            if current_line:
                lines.append(current_line)
                
                current_line=word
    if current_line:
        lines.append(current_line)
    return lines

def create_text_surface(
    text,
    font,
    color,
    max_width,
    line_spacing=8,
    paragraph_spacing=18,
):
    paragraphs = text.split("\n\n")
    rendered_lines = []

    total_height = 0

    for paragraph_index, paragraph in enumerate(paragraphs):
        lines = wrap_text(paragraph, font, max_width)

        for line in lines:
            rendered_lines.append(("line", line))
            total_height += font.get_height() + line_spacing

        if paragraph_index < len(paragraphs) - 1:
            rendered_lines.append(("spacing", None))
            total_height += paragraph_spacing

    if rendered_lines:
        total_height -= line_spacing

    text_surface = pygame.Surface(
        (max_width, total_height),
        pygame.SRCALPHA,
    )

    y_position = 0

    for item_type, content in rendered_lines:
        if item_type == "spacing":
            y_position += paragraph_spacing
            continue

        line_surface = font.render(
            content,
            True,
            color,
        )

        line_rect = line_surface.get_rect(
            centerx=max_width // 2,
            y=y_position,
        )

        text_surface.blit(line_surface, line_rect)
        y_position += font.get_height() + line_spacing

    return text_surface

#DRAWING
def draw_text(screen,text,font,color,x,y):
    surface=font.render(text,True,color)
    screen.blit(surface,(x,y))

def draw_intro_screen(screen,fonts,game_state):
    global BACKGROUND_IMAGE
    
    if BACKGROUND_IMAGE is None:
        BACKGROUND_IMAGE=load_background()
    screen.fill((0, 0, 0))
    
    if BACKGROUND_IMAGE:
        background_copy=BACKGROUND_IMAGE.copy()
        if game_state.intro_phase=="background_fade_in":
            background_copy.set_alpha(game_state.intro_alpha)
    else:
        background_copy.set_alpha(BACKGROUND_MAX_ALPHA)
    screen.blit(background_copy,(0,0))
    
    #dark overlay
    overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA,)
    overlay.fill((0,0,0,185))
    screen.blit(overlay,(0,0))
    
    #Text won't show when background is first fading in 
    if game_state.intro_phase=="background_fade_in":
        return
    current_text=INTRO_SCENES[game_state.intro_scene_index]
    text_surface=create_text_surface(current_text,
                                     fonts["normal"],
                                     (255,255,255),
                                     max_width=320,
                                     line_spacing=10,
                                     )
    text_surface.set_alpha(game_state.intro_alpha)
    text_rect=text_surface.get_rect(center=(WIDTH//2,HEIGHT//2),)
    screen.blit(text_surface,text_rect)
    
    #CONTINUE HINT
    if game_state.intro_phase=="waiting":
        hint_surface=fonts["small"].render("Click to continue",True,(235,235,235))
        #Gentle blinking effect
        hint_alpha=(
            120+int(
                100*abs(
                    pygame.math.Vector2(
                        1,0,
                        ).rotate(
                            pygame.time.get_ticks()/8
                            ).x
                        )
                )
            )
        hint_surface.set_alpha(min(hint_alpha,255))
        hint_rect=hint_surface.get_rect(center=(WIDTH//2,HEIGHT-65),)
        screen.blit(hint_surface,hint_rect)
    
#UPDATING...
def update_intro_screen(game_state):
    if game_state.intro_phase=="background_fade_in":
        game_state.intro_alpha+=FADE_SPEED
        if game_state.intro_alpha>=BACKGROUND_MAX_ALPHA:
            game_state.intro_alpha=0
            game_state.intro_phase="text_fade_in"
    elif game_state.intro_phase=="text_fade_in":
        game_state.intro_alpha+=FADE_SPEED
        if game_state.intro_alpha>=TEXT_MAX_ALPHA:
            game_state.intro_alpha=TEXT_MAX_ALPHA
            game_state.intro_phase="waiting"
    elif game_state.intro_phase=="text_fade_out":
        game_state.intro_alpha-=FADE_SPEED
        if game_state.intro_alpha<=0:
            game_state.intro_alpha=0
            game_state.intro_scene_index+=1
            if(game_state.intro_scene_index>=len(INTRO_SCENES)):
                game_state.current_screen="chat_list"
                return
            game_state.intro_phase="text_fade_in"
    
#INPUT    
def handle_intro_screen_event(event, game_state):
    if game_state.intro_phase!="waiting":
        return
    if event.type==pygame.MOUSEBUTTONDOWN:
        game_state.intro_phase="text_fade_out"
    elif event.type==pygame.KEYDOWN:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE,):
            game_state.intro_phase="text_fade_out"