import pygame
import sys
from copy import deepcopy

from settings import WIDTH, HEIGHT, FPS, create_fonts
from game_state import GameState

from helpers.json_loader import load_chapter

from screens.name_screen import (
    draw_name_screen,
    handle_name_screen_events,
)

from screens.intro_screen import (
    draw_intro_screen,
    handle_intro_screen_event,
    update_intro_screen,
)

from screens.chat_list_screen import (
    draw_chat_list_screen,
    handle_chat_list_event,
)

from screens.chat_screen import (
    draw_chat_screen,
    handle_chat_event,
)

from story_engine import (
    open_conversation,
    handle_player_message_to_martha,
    update_queued_message,
)

from ui.notification import (
    update_notification,
    draw_notification,
    notification_was_clicked,
)

from ui.fade_transition import (
    update_chapter_transition,
    draw_chapter_transition,
)


def handle_debug_keys(event, game_state):
    if event.type != pygame.KEYDOWN:
        return

    # Debug keys only work in chat screen.
    if game_state.current_screen != "chat":
        return

    if event.key == pygame.K_a:
        print("Testing A message")
        handle_player_message_to_martha(
            game_state,
            "What happened to Sarah?"
        )

    elif event.key == pygame.K_s:
        print("Testing S message")
        handle_player_message_to_martha(
            game_state,
            "When did you last see Sarah?"
        )

    elif event.key == pygame.K_d:
        print("Testing D message")
        handle_player_message_to_martha(
            game_state,
            "Martha, you keep avoiding the question. Are you lying to me?"
        )


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("LLM Mystery Game")

    clock = pygame.time.Clock()
    fonts = create_fonts()

    game_state = GameState()
    chapter_data = load_chapter(1)
    game_state.chapter_data = chapter_data
    game_state.messages = deepcopy(
    chapter_data["starting_messages"]
    )

    game_state.unread_counts["Martha"] = len(
    game_state.messages["Martha"]
    )

    game_state.unread_counts["Unknown"] = len(
        game_state.messages["Unknown"]
    )

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if game_state.current_screen == "name_entry":
                handle_name_screen_events(event, game_state)

            elif game_state.current_screen == "intro":
                handle_intro_screen_event(event, game_state)

            elif game_state.current_screen == "chat_list":
                handle_chat_list_event(event, game_state)

            elif game_state.current_screen == "chat":
                handle_chat_event(event, game_state)

            # Notification click
            if game_state.current_screen in ("chat_list", "chat"):
                if notification_was_clicked(event, game_state):
                    sender = game_state.notification["sender"]
                    game_state.notification["visible"] = False
                    open_conversation(game_state, sender)
                    continue

            # Temporary debugging keys: A, S, D
            handle_debug_keys(event, game_state)

        # Update every frame
        update_chapter_transition(game_state)
        update_queued_message(game_state)

        if game_state.current_screen == "intro":
            update_intro_screen(game_state)

        # Draw current screen
        if game_state.current_screen == "name_entry":
            draw_name_screen(screen, fonts, game_state)

        elif game_state.current_screen == "intro":
            draw_intro_screen(screen, fonts, game_state)

        elif game_state.current_screen == "chat_list":
            draw_chat_list_screen(screen, fonts, game_state)

        elif game_state.current_screen == "chat":
            draw_chat_screen(
                screen,
                fonts,
                game_state,
                game_state.messages,
            )

        update_notification(game_state)
        draw_notification(screen, fonts, game_state)
        draw_chapter_transition(screen, game_state)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()