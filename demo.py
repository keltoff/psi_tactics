import pygame

from tile_map import usage_components as uc
from tile_map.data_types.position import Position as Pos
from tile_map.geometry.topology import *
from tile_map.graphics.storage import Storage
from tile_map.gui import Gui
from tile_map.map_display import IsoSketch
from tile_map.map_storage.map_storage import MapSet


if __name__ == '__main__':
    pygame.init()

    display = pygame.display.set_mode((800, 700))
    w, h = display.get_rect().size

    clock = pygame.time.Clock()

    map_store = MapSet()
    map_store.load('data/mapdata.xml')

    sprite_storage = Storage.load('data/graphics_iso.xml')

    cast = uc.CharacterOrganizer()
    cast.add_pc(sprite_storage.make_sprite('war', Pos(13, 5, d=0)))
    cast.add_pc(sprite_storage.make_sprite('jen', Pos(11, 4, d=1)))

    margin = 20
    bottom_bar = 100
    rec1 = pygame.Rect(margin, margin, w - 2* margin, h - 2* margin - bottom_bar)

    disp = IsoSketch(display.subsurface(rec1), map_store['default'], tile_size=30, tilt=60)
    disp.sprites = cast.pcs

    # disp.zones.append(Zone(positions=[Pos(13, 4), Pos(13, 5), Pos(14, 4), Pos(14, 5)], color=pygame.Color(0, 255, 0, 50)))
    #
    # disp.event_pos = lambda pos, etype, button: print('Event at pos {}'.format(pos)) if etype == pygame.MOUSEBUTTONDOWN else ''
    # disp2.event_pos = lambda pos, etype, button: print('Event2 at pos {}'.format(pos)) if etype == pygame.MOUSEBUTTONDOWN else ''

    gui = Gui()
    gui.add(uc.CharacterDisplay(pygame.Rect(margin, h - bottom_bar, 100, bottom_bar-margin), cast))
    # gui.add(disp)
    acs = uc.ActionSelect(pygame.Rect(margin + 200, h-bottom_bar + margin, w - 2*margin, bottom_bar - margin), ['Move', 'Beam', 'Close'])
    gui.add(acs)

    game_over = False
    while not game_over:

        display.fill((0, 0, 0))

        # draw
        gui.draw(display)
        disp.draw()  #should be part pf Gui

        pygame.display.flip()
        clock.tick(15)

        for event in pygame.event.get():
            gui.handle(event)
            disp.handle(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if acs.selected == 'Beam':
                    disp.zones = [Flat4.zone_beam(cast.current_pc.pos, 5).paint('orange')]
                elif acs.selected == 'Close':
                    disp.zones = [Flat8.zone_near(cast.current_pc.pos, 4).paint('blue')]
                else:
                    disp.zones = []

            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_over = True
                if event.key == pygame.K_PAGEUP:
                    cast.prev()
                    disp.center_pos = cast.current_pc.pos
                if event.key == pygame.K_PAGEDOWN:
                    cast.next()
                    disp.center_pos = cast.current_pc.pos

