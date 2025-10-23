import sys
import pygame

from baloon import ALTURA, LARGURA, Balao

BRANCO = (255, 255, 255)
AZUL_CLARO = (173, 216, 230)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
VERDE_ESCURO = (0, 150, 0)
VERDE_CLARO = (0, 200, 0)
CINZA = (150, 150, 150)

MENU = 0
JOGANDO = 1
GAME_OVER = 2


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color,
                 action=None, disabled=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = pygame.font.Font(None, 40)
        self.disabled = disabled

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.disabled:
            cor_atual = CINZA
        else:
            cor_atual = (self.hover_color
                         if self.rect.collidepoint(mouse_pos) else self.color)
        pygame.draw.rect(surface, cor_atual, self.rect)
        text_surf = self.font.render(self.text, True, BRANCO)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return (not self.disabled) and self.rect.collidepoint(pos)


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    relogio = pygame.time.Clock()

    fundo_img = None
    try:
        fundo_original = pygame.image.load("background.jpeg").convert()
        fundo_img = pygame.transform.scale(fundo_original, (LARGURA, ALTURA))
    except pygame.error as exc:
        print("Erro ao carregar o fundo 'background.jpeg':" +
              " %s. Usando cor sólida." % exc)

    title_img = None
    try:
        title_original = pygame.image.load("title.png").convert_alpha()
        max_width = int(LARGURA * 0.8)
        scale = max_width / title_original.get_width()
        title_img = pygame.transform.rotozoom(title_original, 0, scale)
    except pygame.error:
        title_img = None

    balao_unico = Balao()
    todos_sprites = pygame.sprite.Group(balao_unico)

    pontuacao = 0
    pontos_por_clique = 1
    estado_jogo = MENU

    fonte_titulo = pygame.font.Font(None, 84)
    fonte_pontuacao = pygame.font.Font(None, 74)

    def go_to_menu():
        nonlocal estado_jogo
        estado_jogo = MENU

    def start_game():
        nonlocal estado_jogo, pontuacao
        balao_unico.reset()
        pontuacao = 0
        estado_jogo = JOGANDO

    def restart_game():
        start_game()

    def desenhar_texto(superficie, texto, fonte, cor, x, y):
        texto_surface = fonte.render(texto, True, cor)
        texto_rect = texto_surface.get_rect()
        texto_rect.center = (x, y)
        superficie.blit(texto_surface, texto_rect)

    def desenhar_pontuacao():
        desenhar_texto(tela, str(pontuacao), fonte_pontuacao, PRETO,
                       LARGURA // 2, 40)

    def desenhar_fundo():
        if fundo_img:
            tela.blit(fundo_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

    def quit_game():
        pygame.quit()
        sys.exit()

    quit_button = Button(
        LARGURA - 150, 10, 140, 50, "SAIR", VERMELHO, (200, 0, 0),
        action=quit_game
    )
    back_button = Button(
        LARGURA - 150, 10, 140, 50, "VOLTAR", CINZA, (180, 180, 180),
        action=go_to_menu
    )
    start_button = Button(
        LARGURA // 2 - 100, ALTURA // 2, 200, 70, "START", VERDE_ESCURO,
        VERDE_CLARO, action=start_game
    )
    restart_button_go = Button(
        LARGURA // 2 - 120, ALTURA * 3 // 4 - 50, 240, 60, "JOGAR NOVAMENTE",
        VERDE_ESCURO, VERDE_CLARO, action=restart_game
    )

    def desenhar_menu():
        desenhar_fundo()
        if title_img:
            title_rect = title_img.get_rect(
                center=(LARGURA // 2, ALTURA // 4)
            )
            tela.blit(title_img, title_rect)
        else:
            desenhar_texto(
                tela, "Keep Up: O Balão Diagonal", fonte_titulo, PRETO,
                LARGURA // 2, ALTURA // 4
            )
        start_button.draw(tela)
        quit_button.draw(tela)
        pygame.display.flip()

    def desenhar_game_over(pontos):
        tela.fill(PRETO)
        desenhar_texto(tela, "GAME OVER", fonte_titulo, (255, 0, 0),
                       LARGURA // 2, ALTURA // 4)
        desenhar_texto(tela, f"Pontuação da Rodada: {pontos}",
                       fonte_pontuacao, BRANCO, LARGURA // 2, ALTURA // 2 - 40)
        restart_button_go.draw(tela)
        quit_button.draw(tela)
        pygame.display.flip()

    jogo_rodando = True
    while jogo_rodando:
        relogio.tick(60)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                jogo_rodando = False

            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos

                if estado_jogo == JOGANDO:
                    if back_button.is_clicked(pos):
                        back_button.action()
                        continue

                    if balao_unico.foi_clicado(pos):
                        balao_unico.rebater()
                        pontuacao += pontos_por_clique
                        continue

                else:
                    if quit_button.is_clicked(pos):
                        quit_button.action()
                        continue

                    if estado_jogo == MENU:
                        if start_button.is_clicked(pos):
                            start_button.action()

                    elif estado_jogo == GAME_OVER:
                        if restart_button_go.is_clicked(pos):
                            restart_button_go.action()

        if estado_jogo == JOGANDO:
            todos_sprites.update()
            if balao_unico.rect.top > ALTURA:
                estado_jogo = GAME_OVER

            desenhar_fundo()
            todos_sprites.draw(tela)
            desenhar_pontuacao()
            back_button.draw(tela)
            pygame.display.flip()

        elif estado_jogo == MENU:
            desenhar_menu()

        elif estado_jogo == GAME_OVER:
            desenhar_game_over(pontuacao)

    pygame.quit()


if __name__ == "__main__":
    main()
