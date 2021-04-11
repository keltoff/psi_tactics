import pygame

if __name__ == '__main__':
    pygame.init()

    display = pygame.display.set_mode((800, 700))
    w, h = display.get_rect().size

    clock = pygame.time.Clock()


    game_over = False
    while not game_over:

        display.fill((0, 0, 0))

        # draw

        pygame.display.flip()
        clock.tick(15)

        for event in pygame.event.get():
            # handle

            if event.type == pygame.MOUSEBUTTONDOWN:
                pass

            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_over = True
                if event.key == pygame.K_PAGEUP:
                    pass
