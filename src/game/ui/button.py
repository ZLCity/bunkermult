import pygame

class Button:
    """A simple clickable button for UI."""
    def __init__(self, x, y, width, height, text, action=None, action_args=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.action_args = action_args if action_args is not None else []

        # This font is created for every button instance.
        # This is not efficient, but makes the component self-contained for now.
        font = pygame.font.Font(None, 50)

        # Colors are hardcoded for now to keep the class self-contained.
        BLACK = (0, 0, 0)
        LIGHT_GRAY = (170, 170, 170)

        self.text_surf = font.render(self.text, True, BLACK)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.fill_color = LIGHT_GRAY
        self.outline_color = BLACK

    def draw(self, surface):
        """Draws the button on the given surface."""
        pygame.draw.rect(surface, self.fill_color, self.rect)
        pygame.draw.rect(surface, self.outline_color, self.rect, 2)
        surface.blit(self.text_surf, self.text_rect)

    def handle_event(self, event):
        """Handles mouse click events for the button."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action(*self.action_args)
