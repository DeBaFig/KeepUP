from baloon import Balao, LARGURA, ALTURA
import pygame

# --- Constantes ---
BRANCO = (255, 255, 255)
AZUL_CLARO = (173, 216, 230)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
VERDE_ESCURO = (0, 150, 0)
VERDE_CLARO = (0, 200, 0)
CINZA = (150, 150, 150)
AMARELO_OURO = (255, 215, 0)

# --- Estados do Jogo ---
MENU = 0
JOGANDO = 1
GAME_OVER = 2
LOJA = 3 # NOVO ESTADO

# --- Classe do Botão ---
class Button:
    # A classe Button é mantida como está
    def __init__(self, x, y, width, height, text, color, hover_color, action=None, disabled=False):
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
            cor_atual = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        
        pygame.draw.rect(surface, cor_atual, self.rect)
        
        # Desenha o texto do botão
        text_surf = self.font.render(self.text, True, BRANCO)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return not self.disabled and self.rect.collidepoint(pos)


def main():
    pygame.init()
    
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Keep Up: O Balão Diagonal")
    
    relogio = pygame.time.Clock()
    
    # --- Inicialização de Objetos do Jogo ---
    balao_unico = Balao()
    todos_sprites = pygame.sprite.Group(balao_unico)
    
    pontuacao = 0
    dinheiro = 0 # NOVO: Moeda do jogo
    pontos_por_clique = 1 # NOVO: Upgrade de Pontuação
    estado_jogo = MENU
    
    # Fontes
    fonte_titulo = pygame.font.Font(None, 84)
    fonte_pontuacao = pygame.font.Font(None, 74)
    fonte_mensagem = pygame.font.Font(None, 36)
    
    # --- Definição dos Upgrades ---
    # Estrutura: { 'nome': [custo, atributo, valor_efeito, nivel_atual] }
    upgrades = {
        'Gravidade': [50, 'gravidade', -0.1, 0, "Gravidade -10% (Custo: {})"], # Reduz o multiplicador (melhoria)
        'Impulso': [100, 'impulso', 0.15, 0, "Impulso +15% (Custo: {})"],     # Aumenta o multiplicador (melhoria)
        'Tamanho': [150, 'tamanho', 0.1, 0, "Tamanho +10% (Custo: {})"],       # Aumenta o balão
        'Pontos': [200, 'pontos', 1, 0, "Pontos por Clique +1 (Custo: {})"] # Aumenta a pontuação
    }

    # --- Funções de Ação dos Botões ---
    def quit_game():
        nonlocal jogo_rodando
        jogo_rodando = False
        
    def go_to_shop():
        nonlocal estado_jogo
        estado_jogo = LOJA

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
    
    def comprar_upgrade(nome_upgrade):
        nonlocal dinheiro, pontos_por_clique
        upgrade = upgrades[nome_upgrade]
        custo = upgrade[0]
        atributo = upgrade[1]
        valor_efeito = upgrade[2]

        if dinheiro >= custo:
            dinheiro -= custo
            
            # Aplica o efeito no balão ou nas variáveis do jogo
            if atributo in ['gravidade', 'impulso', 'tamanho']:
                balao_unico.aplicar_upgrade(atributo, valor_efeito)
            elif atributo == 'pontos':
                pontos_por_clique += valor_efeito

            # Aumenta o custo para o próximo nível e o nível atual
            upgrade[3] += 1
            upgrade[0] = int(custo * 1.5) # Aumenta o custo em 50%
            print(f"Upgrade '{nome_upgrade}' comprado. Nível: {upgrade[3]}")
        else:
            print("Dinheiro insuficiente!")

    # --- Funções Auxiliares de Desenho ---
    def desenhar_texto(superficie, texto, fonte, cor, x, y):
        texto_surface = fonte.render(texto, True, cor)
        texto_rect = texto_surface.get_rect()
        texto_rect.center = (x, y)
        superficie.blit(texto_surface, texto_rect)

    def desenhar_pontuacao_dinheiro():
        """Desenha a pontuação e o dinheiro na tela de JOGANDO."""
        # Pontuação (pontos por clique na partida atual)
        desenhar_texto(tela, str(pontuacao), fonte_pontuacao, PRETO, LARGURA // 2, 40)
        # Dinheiro Total (Moeda)
        desenhar_texto(tela, f"Dinheiro: {dinheiro}", fonte_mensagem, AMARELO_OURO, LARGURA - 150, 40)

    # --- Funções de Desenho de Estado ---
    
    # Botões Comuns
    quit_button = Button(LARGURA - 150, 10, 140, 50, "SAIR", VERMELHO, (200, 0, 0), action=quit_game)
    
    # Botões do Menu
    start_button = Button(LARGURA // 2 - 100, ALTURA // 2, 200, 70, "START", VERDE_ESCURO, VERDE_CLARO, action=start_game)
    shop_button = Button(LARGURA // 2 - 100, ALTURA // 2 + 100, 200, 70, "LOJA", CINZA, (100, 100, 100), action=go_to_shop)
    
    # Botões da Loja (Criados dinamicamente)
    buy_buttons = []
    
    def desenhar_loja():
        tela.fill(AZUL_CLARO)
        desenhar_texto(tela, "LOJA DE UPGRADES", fonte_titulo, PRETO, LARGURA // 2, 80)
        desenhar_texto(tela, f"Seu Dinheiro: {dinheiro}", fonte_pontuacao, AMARELO_OURO, LARGURA // 2, 160)
        
        # Cria e desenha botões de compra
        buy_buttons.clear()
        y_pos = 250
        
        for nome, data in upgrades.items():
            custo, _, _, nivel, template_texto = data
            
            # Texto
            texto_button = template_texto.format(custo)
            
            # Checa se o jogador pode comprar
            pode_comprar = dinheiro >= custo
            
            # Botão
            button = Button(
                LARGURA // 2 - 250, y_pos, 500, 60, texto_button, 
                VERDE_ESCURO, VERDE_CLARO, action=lambda n=nome: comprar_upgrade(n), 
                disabled=not pode_comprar
            )
            buy_buttons.append(button)
            button.draw(tela)
            
            # Nível Atual
            desenhar_texto(tela, f"Nível: {nivel}", fonte_mensagem, PRETO, LARGURA // 2 + 270, y_pos + 30)

            y_pos += 80

        # Botão de Voltar
        back_button = Button(LARGURA // 2 - 100, ALTURA - 80, 200, 60, "VOLTAR", VERMELHO, (200, 0, 0), action=go_to_menu)
        back_button.draw(tela)
        pygame.display.flip()

    def desenhar_menu():
        tela.fill(AZUL_CLARO)
        desenhar_texto(tela, "Keep Up: O Balão Diagonal", fonte_titulo, PRETO, LARGURA // 2, ALTURA // 4)
        desenhar_texto(tela, "Use o dinheiro para comprar upgrades na loja!", fonte_mensagem, PRETO, LARGURA // 2, ALTURA // 4 + 70)
        
        todos_sprites.draw(tela) # Desenha o balão
        start_button.draw(tela)
        shop_button.draw(tela)
        quit_button.draw(tela)
        pygame.display.flip()

    def desenhar_game_over(pontos):
        tela.fill(PRETO)
        # Transfere a pontuação para o dinheiro
        nonlocal dinheiro
        dinheiro += pontos
        
        desenhar_texto(tela, "GAME OVER", fonte_titulo, (255, 0, 0), LARGURA // 2, ALTURA // 4)
        desenhar_texto(tela, f"Pontuação da Rodada: {pontos}", fonte_pontuacao, BRANCO, LARGURA // 2, ALTURA // 2 - 40)
        desenhar_texto(tela, f"Dinheiro Total: {dinheiro}", fonte_pontuacao, AMARELO_OURO, LARGURA // 2, ALTURA // 2 + 40)
        
        restart_button_go = Button(
            LARGURA // 2 - 120, ALTURA * 3 // 4 - 50, 240, 60, 
            "JOGAR NOVAMENTE", VERDE_ESCURO, VERDE_CLARO, action=restart_game
        )
        restart_button_go.draw(tela)
        
        quit_button.draw(tela)
        pygame.display.flip()

    # --- Loop Principal ---
    jogo_rodando = True
    while jogo_rodando:
        
        relogio.tick(60)

        # 4. Gerenciamento de Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                jogo_rodando = False
                
            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Checa o Botão de Sair em qualquer estado
                if quit_button.is_clicked(pos):
                    quit_button.action()
                    continue
                
                if estado_jogo == JOGANDO:
                    if balao_unico.foi_clicado(pos):
                        balao_unico.rebater()
                        pontuacao += pontos_por_clique # Usa a variável de upgrade
                
                elif estado_jogo == MENU:
                    if start_button.is_clicked(pos):
                        start_button.action()
                    elif shop_button.is_clicked(pos):
                        shop_button.action()
                        
                elif estado_jogo == LOJA:
                    # Checa botões da loja
                    for button in buy_buttons:
                        if button.is_clicked(pos):
                            button.action()
                            break # Apenas um botão pode ser clicado
                    # Checa botão Voltar
                    back_button = Button(LARGURA // 2 - 100, ALTURA - 80, 200, 60, "VOLTAR", VERMELHO, (200, 0, 0), action=go_to_menu)
                    if back_button.is_clicked(pos):
                        back_button.action()
                    
                elif estado_jogo == GAME_OVER:
                    # Re-cria o botão para checar o clique
                    restart_button_go = Button(LARGURA // 2 - 120, ALTURA * 3 // 4 - 50, 240, 60, "JOGAR NOVAMENTE", VERDE_ESCURO, VERDE_CLARO, action=restart_game)
                    if restart_button_go.is_clicked(pos):
                        restart_button_go.action()
                    
        # --- Lógica do Jogo (Update) e Desenho ---
        
        if estado_jogo == JOGANDO:
            todos_sprites.update()

            # Checa se o Balão Caiu
            if balao_unico.rect.top > ALTURA:
                print(f"Game Over! Sua pontuação final é: {pontuacao}")
                estado_jogo = GAME_OVER
                    
            # Desenhar / Renderizar
            tela.fill(AZUL_CLARO)
            todos_sprites.draw(tela)
            desenhar_pontuacao_dinheiro() # NOVO
            quit_button.draw(tela) 
            
            pygame.display.flip()
            
        elif estado_jogo == MENU:
            balao_unico.update() 
            desenhar_menu()
            
        elif estado_jogo == LOJA:
            desenhar_loja()
            
        elif estado_jogo == GAME_OVER:
            desenhar_game_over(pontuacao) # Transfere a pontuação para o dinheiro aqui

    pygame.quit()


if __name__ == "__main__":
    main()