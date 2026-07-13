import pygame

from story_engine import open_conversation
from datetime import datetime

from ui.profile_images import load_profile_image

from settings import(
    BACKGROUND_COLOR,
    BORDER_COLOR,
    HEADER_COLOR,
    PRIMARY_COLOR,
    SECONDARY_TEXT_COLOR,
    TEXT_COLOR,
    UNREAD_COLOR,
    WIDTH,
)

MARTHA_PROFILE=None

MARTHA_CHAT_RECT=pygame.Rect(0,90,WIDTH,90)
UNKNOWN_CHAT_RECT=pygame.Rect(0,180,WIDTH,90)

def draw_text(screen,text,font,color,x,y):
    text_surface=font.render(text,True,color)
    screen.blit(text_surface,(x,y))
    
def draw_circular_profile(screen,image,center,radius,fallback_text="?",
                          fallback_color=(65,105,225)):
    if not isinstance(image,pygame.Surface):
        pygame.draw.circle(
            screen,
            fallback_color,
            center,
            radius
        )
        fallback_surface=pygame.font.Font(None,28).render(
            fallback_text,
            True,
            (255,255,255),
        )
        screen.blit(fallback_surface,
                    fallback_surface.get_rect(center=center),)
        return

    diameter=radius*2
    scaled_image=pygame.transform.smoothscale(
        image,
        (diameter,diameter),
    )
    mask=pygame.Surface(
    (diameter,diameter),
    pygame.SRCALPHA,
    )
    pygame.draw.circle(
        mask,
        (255,255,255,255),
        (radius,radius),
        radius,
    )
    circular_image=scaled_image.copy()
    circular_image.blit(mask,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(
        circular_image,
        (center[0]-radius,center[1]-radius),
    )
    
def draw_chat_list_item(
    screen,
    fonts,
    rect,
    name,
    preview,
    status_text,
    unread_count=0,
    profile_image=None,
):
    pygame.draw.rect(screen,HEADER_COLOR,rect)
    pygame.draw.line(
        screen,
        BORDER_COLOR,
        (20,rect.bottom),
        (WIDTH,rect.bottom),
        1,
    )
    profile_center=(45,rect.y+45)
    draw_circular_profile(
        screen,
        profile_image,
        profile_center,
        27,
        fallback_text=name[0]
    )
    if profile_image is None:
        initial_surface=fonts["normal"].render(
            name[0],
            True,
            (255,255,255),
        )
        screen.blit(
            initial_surface,
            initial_surface.get_rect(center=profile_center),
        )

    draw_text(
        screen,
        name,
        fonts["normal"],
        TEXT_COLOR,
        85,
        rect.y + 12,
    )
    draw_text(
        screen,
        preview,
        fonts["small"],
        SECONDARY_TEXT_COLOR,
        85,
        rect.y+42,
    )
    draw_text(
        screen,
        status_text,
        fonts["small"],
        SECONDARY_TEXT_COLOR,
        85,
        rect.y + 65,
    )
    if unread_count>0:
       badge_center = (357, rect.y + 45)

       pygame.draw.circle(
            screen,
            UNREAD_COLOR,
            badge_center,
            14,
        )

       count_surface = fonts["small"].render(
            str(unread_count),
            True,
            (255, 255, 255),
        )

       screen.blit(
            count_surface,
            count_surface.get_rect(center=badge_center),
        )
def draw_chat_list_screen(screen,fonts,game_state):
    global MARTHA_PROFILE
    if MARTHA_PROFILE is None:
        MARTHA_PROFILE=load_profile_image("martha_pp.png",54,)
        print("Martha profile loaded:", isinstance(MARTHA_PROFILE,pygame.Surface),)
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(
        screen,
        HEADER_COLOR,
        pygame.Rect(0,0,WIDTH,90),
    )
    
    draw_text(
        screen,
        "Messages",
        fonts["title"],
        TEXT_COLOR,
        20,
        30,
    )
    draw_chat_list_item(
        screen,
        fonts,
        MARTHA_CHAT_RECT,
        "Martha",
        get_last_message_preview(game_state, "Martha"),
        get_contact_status_text(game_state, "Martha"),
        game_state.unread_counts["Martha"],
        profile_image=MARTHA_PROFILE
    )
    if game_state.unknown_unlocked:
        draw_chat_list_item(
            screen,
            fonts,
            UNKNOWN_CHAT_RECT,
            "Unknown",
            get_last_message_preview(game_state, "Unknown"),
            get_contact_status_text(game_state, "Unknown"),
            game_state.unread_counts["Unknown"],
            profile_image=None,
        )

def handle_chat_list_event(event,game_state):
    if event.type!=pygame.MOUSEBUTTONDOWN:
        return
    if MARTHA_CHAT_RECT.collidepoint(event.pos):
        open_conversation(game_state, "Martha")

    elif (game_state.unknown_unlocked and UNKNOWN_CHAT_RECT.collidepoint(event.pos)):
        open_conversation(game_state, "Unknown")
def get_last_message_preview(game_state, contact_name):
    contact_messages = game_state.messages[contact_name]

    if not contact_messages:
        return "No messages yet."

    text = contact_messages[-1]["text"]

    if len(text) > 34:
        return text[:31] + "..."

    return text


def get_contact_status_text(game_state, contact_name):
    status = game_state.contact_status[contact_name]

    if status["is_typing"]:
        return "Typing..."

    if status["is_active"]:
        return "Active now"

    if status["last_seen"] is None:
        return "Offline"

    last_seen_time = datetime.fromtimestamp(
        status["last_seen"]
    ).strftime("%I:%M %p")

    return f"Last seen {last_seen_time}"

