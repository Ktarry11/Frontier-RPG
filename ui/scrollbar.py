"""One scrollbar for every scrolling list: drawn in its own gutter, and draggable.

Kyle, 14 Nov 2026: "for a lot of the menus, where there is a slider to drag down, it overlaps with
the right side of the item so you can't actually use it... I notice it in shops when buying."

He was right on both counts. The shop, the quest log and the bags each drew a thin track ON TOP of
the right edge of their rows, so a click aimed at it landed on the row underneath, and in the shop
and the bags the bar was only a picture: nothing listened for a click or a drag on it at all.

So: a list that scrolls keeps GUTTER pixels clear on its right for the bar (rows end before it),
and the bar takes clicks. Click the thumb and drag it, or click the track to jump there. The
mouse wheel still works as before; this only adds the bar.

Usage, per list, with scroll measured in whatever steps the list already uses (rows):

    self.bar = ScrollBar()
    # render:
    self.bar.draw(screen, track_rect, scroll, max_scroll, visible)
    # handle_event, before the rows get the click:
    new = self.bar.handle_event(event, scroll)
    if new is not None:
        self.scroll = new
        return
"""
import pygame

#: pixels a scrolling list leaves clear on its right for the bar
GUTTER = 16
#: how wide the bar is drawn (it takes clicks a few pixels either side too)
WIDTH = 10

TRACK = (34, 34, 42)
THUMB = (125, 125, 145)
THUMB_HOT = (200, 180, 110)


class ScrollBar:
    def __init__(self):
        self.track = pygame.Rect(0, 0, 0, 0)
        self.thumb = pygame.Rect(0, 0, 0, 0)
        self.max_scroll = 0
        self.dragging = False
        self._grab = 0          # where on the thumb it was picked up

    @staticmethod
    def track_for(area):
        """The track rect for a list occupying `area`: its right-hand gutter."""
        return pygame.Rect(area.right - GUTTER + (GUTTER - WIDTH) // 2, area.y, WIDTH, area.height)

    def draw(self, screen, track, scroll, max_scroll, visible):
        """Draw the bar, or nothing (and take no clicks) when everything fits."""
        self.track = pygame.Rect(track)
        self.max_scroll = max(0, int(max_scroll))
        if self.max_scroll <= 0 or self.track.height <= 0:
            self.thumb = pygame.Rect(0, 0, 0, 0)
            self.dragging = False
            return
        pygame.draw.rect(screen, TRACK, self.track, border_radius=4)
        visible = max(1, visible)
        h = max(28, int(self.track.height * visible / (visible + self.max_scroll)))
        h = min(h, self.track.height)
        span = self.track.height - h
        y = self.track.y + int(span * max(0, min(scroll, self.max_scroll)) / self.max_scroll)
        self.thumb = pygame.Rect(self.track.x, y, self.track.width, h)
        hot = self.dragging or self.thumb.inflate(8, 0).collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, THUMB_HOT if hot else THUMB, self.thumb, border_radius=4)

    def _scroll_at(self, thumb_top):
        span = self.track.height - self.thumb.height
        if span <= 0:
            return 0
        frac = (thumb_top - self.track.y) / span
        return int(round(max(0.0, min(1.0, frac)) * self.max_scroll))

    def hit(self, pos):
        return self.max_scroll > 0 and self.track.inflate(8, 0).collidepoint(pos)

    def handle_event(self, event, scroll):
        """The new scroll position if the bar used this event, else None (so the caller carries on
        and the click can reach a row)."""
        if self.max_scroll <= 0:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", 1) == 1 and self.hit(event.pos):
            self.dragging = True
            if self.thumb.inflate(8, 0).collidepoint(event.pos):
                self._grab = event.pos[1] - self.thumb.y
                return scroll
            # a click on the track: jump so the thumb is centred there, then keep dragging
            self._grab = self.thumb.height // 2
            return self._scroll_at(event.pos[1] - self._grab)
        if event.type == pygame.MOUSEMOTION and self.dragging:
            return self._scroll_at(event.pos[1] - self._grab)
        if event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            return scroll
        return None
