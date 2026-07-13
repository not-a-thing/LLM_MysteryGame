from pathlib import Path
import pygame

def load_profile_image(filename,size):
    image_path=(Path(__file__).resolve().parent.parent
                /'assets'
                /"images"
                /filename)
    try:
        image=pygame.image.load(str(image_path)).convert_alpha()
        return pygame.transform.smoothscale(image,(size,size))
    except (pygame.error,FileNotFoundError) as error:
        print(f"could not load {filename}:", error)
        return None