import pygame
from network import Network
from button import Button
from deck import Deck
import pygame.gfxdraw
import socket, pickle
from lobby import Lobby  # required module
from game import Game  # required module

width = 800
height = 800
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Big Two")
pygame.font.init()

btn_w = width // 5
btn_h = height // 8

red = (255, 0, 0)
white = (255, 255, 255)
green = (0, 150, 55)
black = (0,0,0)
blue = (0,0,180)
yellow = (255,255,123)

w, h = pygame.display.get_surface().get_size()

clock = pygame.time.Clock()
n = None

card_dict = {}


def verify_hand(hand, hand_type, game):
    if hand_type == 0:  # Played nothing
        return False
    elif game.play_type != 0 and hand_type != game.play_type and not hand_type >= 5:  # If hand isn't same or super
        return False

    hand_played = []
    for index, card in enumerate(hand):  # Append only the card
        hand_played.append(card[0])
        print(hand_played[index])

    if game.first_play and game.first_play_card not in hand_played:  # Smallest card must be played first
        print(f'Must play {game.first_play_card}')
        return False
    if game.play_type == 0 and hand_type >= 1:  # If previous play doesn't exist
        return True
    if game.play_type == 0:  # No previous winning hand
        print("No previous winning hand")
    elif hand_type >= 5:  # If hand_type is fours or straight flush
        if game.play_type <= 4:  # If previous play isn't a super hand
            return True
        if game.play_type == 5 and hand_type == 6:  # Fours < Straight Flush
            return True
        if game.play_type == 6 and hand_type == 5:  # Straight Flush > Fours
            return False
        else:
            print("Both hands are the same super!")
            pass
    if hand_type == 2:  # Pair
        if hand_played[1].rank > game.hand_played[1].rank:
            print("Rank was bigger (Double)")
            return True
        elif hand_played[1].rank == game.hand_played[1].rank:  # If ranks are equal
            if hand_played[1].suit > game.hand_played[1].suit:
                print("Suit was bigger (Double)")
                return True
        else:
            print("Card played was smaller (Double)")
            return False
    elif hand_type == 4:  # Full House
        if hand_played[2].rank > game.hand_played[2].rank:  # Card at index 2 will always be a card of three
            print("Rank was bigger (Full House)")
            return True
        else:
            return False
    else:  # Single, Straight, Fours, and Straight Flush
        last_card = hand_played[len(hand_played) - 1]
        prev_last_card = game.hand_played[len(game.hand_played) - 1]
        print(f"Compare {last_card} to {prev_last_card}")
        if last_card.rank > prev_last_card.rank:
            print("Rank bigger (Last Case)")
            print(f"{last_card.rank} > {prev_last_card.rank}")
            return True
        elif last_card.rank == prev_last_card.rank and last_card.suit > prev_last_card.suit:
            print("Suit bigger (Last Case)")
            return True
        else:
            print("Played hand is smaller (Last Case)")
            return False
    print("Shouldn't reach this print line")


def draw_hand_played(game, card_size):
    global width
    global height
    center_space = len(game.hand_played) * card_size[0]
    center_x = width / 2 - center_space / 2
    center_y = height / 2 - card_size[1] / 2
    hand_played = game.hand_played.copy()

    x = x1 = center_x
    y = center_y
    for index, card in enumerate(hand_played):
        hand_played[index] = card_dict[card]
        draw(hand_played[index], x, y)
        x += center_space / len(game.hand_played)


def update_card_space(x1, game, player_num, card_size):
    print(f'Player\'s length is {len(game.players[player_num].hand)}')
    card_space = int((width - x1 * 2) / len(game.players[player_num].hand))
    return card_space


def draw_opp(image, game, player_num):
    img_size = image.get_rect().size
    rotated_image = pygame.transform.rotate(image, 90)
    global width, height, btn_h
    p1 = player_num

    p2_x = width - img_size[1]
    p2_y = p2_y1 = img_size[1]

    font = pygame.font.SysFont('arial', btn_h // 4)
    text_color = white
    txt_w, txt_h = font.render("Player #", 1, white).get_rect().size

    side = 0
    for index, player in enumerate(game.players):
        if game.current_player == player.player:
            text_color = yellow
        text = font.render(f"Player {player.player}", 1, text_color)
        txt_w, txt_h = text.get_rect().size

        if index == p1:
            window.blit(text, (width // 2 - txt_w // 2, height - img_size[1] * 2 - txt_h - 10))
            text_color = white
            continue
        elif side == 0 and not (game.players[index].finish or game.players[index].quit):  # P2
            x = width - img_size[1]
            y = y1 = img_size[1]
            for card in game.players[index].hand:
                draw(rotated_image, x, y)
                y += (height - y1 - img_size[0] * 2) / len(game.players[index].hand)
            window.blit(text, (x - txt_w - 10, height // 2 - txt_h // 2))
        elif side == 1 and not (game.players[index].finish or game.players[index].quit):
            x = 0
            y = y1 = img_size[1]
            for card in game.players[index].hand:
                draw(rotated_image, x, y)
                y += (height - y1 - img_size[0] * 2) / len(game.players[index].hand)
            window.blit(text, (img_size[1] + 10, height // 2 - txt_h  // 2))
        elif side == 2 and not (game.players[index].finish or game.players[index].quit):
            y = 0
            x = x1 = img_size[1]
            for card in game.players[index].hand:
                draw(image, x, y)
                x += (width - x1 - img_size[0] * 2) / len(game.players[index].hand)
            window.blit(text, (width // 2 - txt_w // 2, img_size[1] + txt_h + 10))
        text_color = white
        side += 1


def get_overlap(card_width, card_space):
    return card_width - card_space


def load_images():
    deck = Deck()
    for card in deck.deck:
        text = str(card).split(' of ')
        if text[0].isdigit():
            file_name = text[0] + text[1][0] + '.png'
        else:
            file_name = text[0][0] + text[1][0] + '.png'
        card_dict[card] = file_name


def draw(image, x, y):
    window.blit(image, (x, y))


def resize_card(file):
    global width, height
    img_size = pygame.image.load(file).get_rect().size
    if width == height:
        print("Window is symmetrical")
        img_size = (int(img_size[0] / (w * 0.0125)), int(img_size[1] / (h * 0.0125)))
    else:
        print("Window isn't symmetrical")
        img_size = (int(img_size[1] / (h * 0.0125)), int(img_size[1] / (h * 0.0125)))
    image = pygame.image.load(file)
    image = pygame.transform.scale(image, (img_size[0], img_size[1]))
    return image


def equalize_image(file, card_w, card_h):
    image = pygame.image.load(file)
    image = pygame.transform.scale(image, (card_w, card_h))
    return image


def disconnect(n):
    print("Disconnected from server")
    n.disconnect()
    return False


def game_over_screen(game, window, player_num, lobby):
    print("Game over screen")
    touched = False
    pygame.font.init()
    global width
    global height

    font = pygame.font.SysFont("arial", 18)
    texts = []
    place = ['1st', '2nd', '3rd', '4th']
    for index, finished_player in enumerate(game.finished_players):
        texts.append(font.render(f"{place[index]} place: Player {finished_player.player}", True, white))

    txt_height = texts[0].get_height()
    txt_width = texts[0].get_width()
    y1 = height // 3 - txt_height * 2
    y2 = height // 3
    y3 = height // 3 + txt_height * 2
    y4 = height // 3 + txt_height * 4

    while not touched:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                n.send(str(["leave", player_num, lobby]))
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                touched = True
                break

        window.fill(green)
        for index, player in enumerate(game.finished_players):
            if index == 0:
                window.blit(texts[index], (width // 2 - txt_width // 2, y1))
            if index == 1:
                window.blit(texts[index], (width // 2 - txt_width // 2, y2))
            if index == 2:
                window.blit(texts[index], (width // 2 - txt_width // 2, y3))
            if index == 3:
                window.blit(texts[index], (width // 2 - txt_width // 2, y4))

        pygame.display.update()
    print("Returning to lobby...")


def play_game(lobby, player_num):
    run = True

    print('Game play')
    window.fill(green)
    pygame.display.update()

    load_images()
    game = n.send('get')

    player_num = game.get_index(player_num)

    if game is None:
        print('Game is empty')

    hand = game.players[player_num].hand
    print(game.players[player_num])
    print(game.__sizeof__())

    card_size = resize_card('3C.png').get_rect().size
    for index, card in enumerate(hand):
        hand[index] = (card, resize_card(card_dict[card]))
    for card in card_dict:
        card_dict[card] = resize_card(card_dict[card])

    card_back = equalize_image('back.png', card_size[0], card_size[1])
    x = x1 = card_size[0]
    y = height - card_size[1]
    card_space = int((width - x1 * 2) / len(game.players[player_num].hand))
    overlap_space = get_overlap(card_size[0], card_space)
    card_button = []
    for num, card in enumerate(hand):
        draw(card[1], x, y)
        if num == len(hand) - 1:
            overlap_space = 0
        card_button.append(Button(str(num), x, y, (0, 0, 0, 0), card_size[0] - overlap_space, card_size[1], True))
        x += card_space

    global btn_w, btn_h
    play_button = Button('Play', card_size[1], height - (card_size[1] * 2 + btn_h), red, btn_w, btn_h, False)
    pass_button = Button('Pass', width - (card_size[1] + btn_w), height - (card_size[1] * 2 + btn_h), blue,
                         btn_w, btn_h, False)
    play_hand = []  # Played cards index
    finished = False

    while run:
        clock.tick(30)

        try:
            game = n.send('get')
        except EOFError as e:
            run = False
            print("Couldn't get game")
            print(e)
            break

        window.fill(green)
        play_button.draw(window)
        pass_button.draw(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                n.send(str(["leave", player_num, lobby]))
                run = False
                pygame.quit()
            # Button Press
            if event.type == pygame.MOUSEBUTTONDOWN and not finished:
                pos = pygame.mouse.get_pos()
                if play_button.click(pos):  # Play
                    play_button.darken_button()
                if pass_button.click(pos):  # Show
                    pass_button.darken_button()
                for index, button in enumerate(card_button):
                    if button.click(pos):  # Button
                        if button.y == button.initial_y:
                            button.y -= card_size[1]
                            play_hand.append(index)
                        else:
                            button.y = button.initial_y
                            play_hand.remove(index)
                        print(play_hand)
            if event.type == pygame.MOUSEBUTTONUP and not finished:
                pos = pygame.mouse.get_pos()
                if play_button.click(pos) and play_button.is_held_down:
                    if player_num != game.current_player:
                        print('Not your turn!')
                        play_button.lighten_button()
                    else:
                        # Setup
                        temp_hand = play_hand.copy()
                        hand_copy = hand.copy()
                        temp_hand.sort()
                        print(f'Temp_hand: {temp_hand}')
                        for index, card in enumerate(play_hand):  # Converts hand index to card
                            card_played = hand[card]
                            play_hand[index] = card_played[0]
                        # Hand check
                        hand_type = game.check_hand(play_hand)
                        hand_tester = []
                        for card in temp_hand:
                            hand_tester.append(hand_copy[card])
                        if not verify_hand(hand_tester, hand_type, game):  # If not a valid hand, return cards
                            print("Hand doesn't pass test!")
                            play_hand.clear()
                            temp_hand.clear()
                            hand_copy.clear()
                            for button in card_button:
                                button.reset_pos()
                            pass_button.lighten_button()
                            continue
                        # Passes all checks
                        game = n.send(str(temp_hand))
                        # Update
                        for index in reversed(temp_hand):  # Remove cards by index
                            del hand[index]
                            del card_button[index]
                        if len(hand) == 0:  # If finished, loop
                            print("Hand cleared!")
                            finished = True
                            continue
                        print(game.players[player_num])  # Prints current hand TODO: Delete later
                        card_space = update_card_space(x1, game, player_num, card_size)
                        for button in card_button:
                            button.reset_pos()
                            button.update_width(card_space, card_size[0])
                        play_hand.clear()
                        temp_hand.clear()
                        play_button.lighten_button()
                elif not play_button.click(pos) and play_button.is_held_down:
                    play_button.lighten_button()
                if pass_button.click(pos) and pass_button.is_held_down:
                    if player_num != game.current_player:
                        print("Not your turn!")  # TODO change to text box
                    elif game.play_type == 0:
                        print("You must play a card!")  # TODO change to text box
                    else:
                        n.send('pass')
                    pass_button.lighten_button()
                elif not pass_button.click(pos) and pass_button.is_held_down:
                    pass_button.lighten_button()

        # Display board
        draw_opp(card_back, game, player_num)
        x = x1 = card_size[0]
        y = height - card_size[1]
        if not finished:
            for num, card in enumerate(hand):  # Draw button selection box
                if num == len(hand) - 1:  # Check if last card in hand
                    card_button[num].width = card_size[0]
                if card_button[num].at_diff_pos():  # Deselect card
                    draw(card[1], x, y - card_size[1])
                else:
                    draw(card[1], x, y)
                card_button[num].update_x(x)
                card_button[num].draw(window)

                x += card_space
            x = x1
        draw_hand_played(game, card_size)

        if game.game_finished:
            run = False
            break

        pygame.display.update()

    print("Concluding game")
    game_over_screen(game, window, player_num, lobby)
    return lobby


def join_lobby(player_num, lobby):
    run = True
    global width, height
    print("Joined lobby")

    key = lobby.get_number()
    lobby = None

    start_button = Button("Start", width - btn_w, height - btn_h, white, btn_w, btn_h, False)
    ready_button = Button("Ready", width // 2 - btn_w // 2, height - btn_h, white, btn_w, btn_h, False)
    back_button = Button("Back", 0, height - btn_h, white, btn_w, btn_h, False)

    font = pygame.font.SysFont("arial", height // 15)
    crown = pygame.image.load("crown.png")

    print(f"You are player {player_num}")

    while run:
        clock.tick(30)
        window.fill(green)

        start_button.draw(window)
        ready_button.draw(window)
        back_button.draw(window)

        lobby = n.send_object((key, "key"))

        for player in lobby.players:
            if player is None: continue
            x = 60
            y1 = height // 2
            y = y1 * (0.25 * (player + 1))
            text_x = width - font.render("Ready", 1, white).get_width() - 20

            window.blit(font.render(f"Player {player}", 1, white), (x, y))
            if lobby.ready[player]:
                window.blit(font.render("Ready", 1, white), (text_x, y))
            if player == lobby.get_host():
                window.blit(crown, (0, y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                n.send_object(((key, player_num), "quit"))
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if start_button.click(pos) and lobby.get_host() == player_num:
                    start_button.darken_button()
                if ready_button.click(pos):
                    ready_button.darken_button()
                if back_button.click(pos):
                    back_button.darken_button()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if start_button.click(pos) and start_button.is_held_down:  # Start
                    if lobby.start_game():
                        n.send_object((key, "start"))
                    start_button.lighten_button()
                elif not start_button.click(pos) and start_button.is_held_down:
                    start_button.lighten_button()
                if ready_button.click(pos) and ready_button.is_held_down:  # Ready
                    n.send_object(((key, player_num), "ready"))
                    ready_button.lighten_button()
                elif not ready_button.click(pos) and ready_button.is_held_down:
                    ready_button.lighten_button()
                if back_button.click(pos) and back_button.is_held_down:  # Back
                    n.send_object(((key, player_num), "quit"))
                    print("Returning to lobby")
                    return
                elif not back_button.click(pos) and back_button.is_held_down:
                    back_button.lighten_button()

        pygame.display.update()

        if lobby.start:
            lobby = n.send_object((key, "key"))
            n.send_object((key, "game"))
            key = play_game(key, player_num)
            lobby = n.send_object((key, "key"))
            pygame.font.init()
            print("Returned to lobby")
            print(lobby)


def input_text(box, font, y):
    print("Now inputting text")

    text_input = ""
    typing = True
    pos = None
    while typing:
        box.draw(window)
        for event in pygame.event.get():  # TODO What if the user clicks out?
            if event.type == pygame.QUIT:
                typing = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.unicode.isalpha() or event.unicode.isdigit():
                    text_input += event.unicode
                elif event.key == pygame.K_SPACE:
                    text_input += " "
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                elif event.key == pygame.K_RETURN:
                    typing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(f"Pos set to {pos}")
                if not box.click(pos):
                    typing = False
        rendered_text = font.render(text_input, 1, white)
        window.blit(rendered_text, (40, y))
        pygame.display.update()
    print(f"Inputted {text_input}")
    return text_input, pos


def create_menu():
    run = True
    global width
    global height

    box_width = width - 40
    box_height = height // 10

    font = pygame.font.SysFont("arial", box_height // 2)
    room_name = font.render('Name here', 1, white)
    password = font.render('', 1, white)

    #  TODO Check these boxes later
    room_black_box = Button("", 20, 100, black, box_width, box_height, False)
    pass_black_box = Button("", 20, 300, black, box_width, box_height, False)
    create_button = Button("Create", width // 2 - 75, height * 0.75, white, 150, 100, False)
    room_text_y = 100 + box_height // 2 - room_name.get_height() // 2
    password_y = 300 + box_height // 2 - password.get_height() // 2
    name_text = font.render("Name:", 1, white)
    pass_text = font.render("Password:", 1, white)

    out1 = out2 = ''
    click_out = None

    while run:
        clock.tick(30)

        window.fill(green)
        room_black_box.draw(window)
        pass_black_box.draw(window)
        create_button.draw(window)
        window.blit(name_text, (width // 2 - name_text.get_size()[0] // 2, room_black_box.rect.top - name_text.get_size()[1]))
        window.blit(pass_text, (width // 2 - pass_text.get_size()[0] // 2, pass_black_box.rect.top - pass_text.get_size()[1]))
        window.blit(room_name, (40, room_text_y))
        window.blit(password, (40, password_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if room_black_box.click(pos):
                    text_input, click_out = input_text(room_black_box, font, room_text_y)
                    out1 = text_input
                    room_name = font.render(text_input, 1, white)
                    print(click_out)
                if pass_black_box.click(pos):
                    text_input, click_out = input_text(pass_black_box, font, password_y)
                    out2 = text_input
                    password = font.render(text_input, 1, white)
                if create_button.click(pos):
                    create_button.darken_button()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if create_button.click(pos) and create_button.is_held_down:
                    print(f"Room name: {out1}, Password: {out2}")
                    return out1, out2
                elif not create_button.click(pos) and create_button.is_held_down:
                    create_button.lighten_button()

        # When user clicks out while inputting text, do the same as above
        while click_out is not None:
            if room_black_box.click(click_out):
                text_input, click_out = input_text(room_black_box, font, room_text_y)
                out1 = text_input
                room_name = font.render(text_input, 1, white)
            if pass_black_box.click(click_out):
                text_input, click_out = input_text(pass_black_box, font, password_y)
                out2 = text_input
                password = font.render(text_input, 1, white)
            if create_button.click(click_out):
                print(f"Room name: {out1}, Password: {out2}")
                return out1, out2
            else:
                click_out = None
                break

        pygame.display.update()


def display_lobby(lobby, buttons, page, rpp):  # 6 Rooms per a page. Cut to 5 if other sizes dont work
    global width, height
    box_width = width - 40
    box_height = height // 10
    x = 20
    y = 20

    font = pygame.font.SysFont("arial", box_height // 2)
    lock_font = pygame.font.SysFont("arial", box_height // 3)
    locked_text = lock_font.render("Locked", 1, red)

    rooms = []
    for key in lobby.keys():
        if not lobby[key].start:
            rooms.append(key)
    room_page = rooms[page * rpp:page * rpp + rpp]
    for room in room_page:
        pygame.draw.rect(window, black,(x, y, box_width, box_height))
        name = font.render(lobby[room].get_name(), 1, white)
        window.blit(name, (x + 10, y + box_height // 2 - name.get_height() // 2))

        button = Button("Join", width - 130, y + 10, (105,105,105), 100, box_height - 20, False)  # TODO Check later
        button.set_key(room)
        buttons.append(button)
        button.draw(window)

        if lobby[room].get_password() != '':
            window.blit(locked_text,
                        (button.x - locked_text.get_width(), y + box_height // 2 - locked_text.get_height() // 2))

        y += box_height + 20


def enter_password(key):
    run = True
    global width, height
    rect = pygame.Rect(0, 0, width, height)
    color = (100,100,100,5)

    black_box = Button("", 20, height // 2 - height // 10, black, width - 40, height // 10, False)
    font = pygame.font.SysFont("arial", black_box.height // 2)
    password_prompt = font.render("Password:", 1, white)
    text_height = password_prompt.get_height()

    while run:
        clock.tick(30)
        pygame.gfxdraw.box(window, rect, color)
        black_box.draw(window)

        window.blit(password_prompt, (20, black_box.y - text_height - 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if black_box.click(pos):
                    print("Selected black box")
                    text_input = input_text(black_box, font, black_box.y + black_box.height // 2 - text_height // 2)[0]
                    print(text_input)
                    return n.send_object(((key, text_input), "password")) # Receives boolean from server

        pygame.display.update()


def server_menu():  # Get a list of all available rooms by connecting to network
    run = True
    lobby = room = None
    global n

    create_button = Button("Create", width - btn_w, height - btn_h, white, btn_w, btn_h, False)
    refresh_button = Button("Refresh", width // 2 - btn_w // 2, height - btn_h, white, btn_w, btn_h, False)
    back_button = Button("Back", 0, height - btn_h, white, btn_w, btn_h, False)
    next_button = Button("Next", width - btn_w, height - btn_h * 3 - 20, blue, btn_w, btn_h, False)
    prev_button = Button("Prev", 0, height - btn_h * 3 - 20, blue, btn_w, btn_h, False)

    try:
        n = Network()
        n.connect()
        lobby = dict(n.send_object("get"))
    except:
        print("No connection")
        n.disconnect()
        return False

    print(lobby.__sizeof__())
    print(f"There are {len(lobby)} rooms in the lobby")

    join_buttons = []
    page = 0
    rpp = next_button.rect.top // ((height // 10) + 20)  # Rooms per page

    font = pygame.font.SysFont('arial', btn_h // 4)
    pages = None

    while run:
        clock.tick(30)
        window.fill(green)

        create_button.draw(window)
        refresh_button.draw(window)
        back_button.draw(window)
        if len(lobby) / rpp > 1:
            pages = font.render(f"{page}/{len(lobby) // rpp}", 1, white)
            next_button.draw(window)
            prev_button.draw(window)
            window.blit(pages, (width // 2 - pages.get_rect().width // 2,
                                next_button.y + btn_h // 2 - pages.get_rect().height))

        display_lobby(lobby, join_buttons, page, rpp)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if create_button.click(pos):
                    create_button.darken_button()
                if refresh_button.click(pos):
                    refresh_button.darken_button()
                if back_button.click(pos):
                    back_button.darken_button()
                if next_button.click(pos):
                    next_button.darken_button()
                if prev_button.click(pos):
                    prev_button.darken_button()
                for button in join_buttons:
                    if button.click(pos):
                        key = button.get_key()
                        if lobby[key].is_pass_protected():
                            print("Room is password protected")
                            password_correct = enter_password(key)  # Boolean if password is correct
                            if not password_correct:
                                print("Incorrect password")
                                continue
                        print(f"Joining room {key}... \'{lobby[key].get_name()}\'")
                        room, player_num = n.send_object((key, 'join'))
                        if room in ["Failure", "In-progress", "Empty"]:
                            print(f"Game is {room}! Refreshing...")
                            lobby = dict(n.send_object("get"))
                            continue
                        pygame.time.wait(500)
                        # button.darken_button()  # This button won't darken
                        join_lobby(player_num, room)
                        lobby = dict(n.send_object("get"))
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if create_button.click(pos) and create_button.is_held_down:
                    data = create_menu()
                    print(f"Sending data: {data}")
                    try:
                        room = n.send_object(data + ('create',))
                    except EOFError as e:
                        print("Failed to send room creation info!")
                        print(e)
                        return disconnect(n)
                    pygame.time.delay(1000)
                    player_num = room.get_host()
                    print(f"You are player {player_num}")
                    join_lobby(player_num, room)
                    try:
                        lobby = dict(n.send_object("get"))
                    except:
                        print("Failed to join lobby after creation!")
                        return disconnect(n)
                    create_button.lighten_button()
                elif not create_button.click(pos) and create_button.is_held_down:
                    create_button.lighten_button()
                if refresh_button.click(pos) and refresh_button.is_held_down:
                    try:
                        lobby = dict(n.send_object("get"))
                    except:
                        print("Failed to refresh lobby!")
                        return disconnect(n)
                    page = 0
                    refresh_button.lighten_button()
                elif not refresh_button.click(pos) and refresh_button.is_held_down:
                    refresh_button.lighten_button()
                if back_button.click(pos) and back_button.is_held_down:
                    run = False
                    n.disconnect()
                    return True
                elif not back_button.click(pos) and back_button.is_held_down:
                    back_button.lighten_button()
                if next_button.click(pos) and next_button.is_held_down:
                    if page == len(lobby) // rpp or (page + 1 == len(lobby) // rpp and len(lobby) % rpp == 0):
                        print("Go to 0")
                        page = 0
                    else:
                        print("Increment page")
                        page += 1
                    next_button.lighten_button()
                    print(f"Forward to page {page}")
                elif not next_button.click(pos) and next_button.is_held_down:
                    next_button.lighten_button()
                if prev_button.click(pos) and prev_button.is_held_down:
                    if page == 0 and not len(lobby) == rpp:
                        print("Go to last page")
                        page = len(lobby) // rpp
                    elif len(lobby) > rpp:
                        print("Decrement page")
                        page -= 1
                    else:
                        break
                    prev_button.lighten_button()
                    print(f"Back to page {page}")
                elif not prev_button.click(pos) and prev_button.is_held_down:
                    prev_button.lighten_button()

        pygame.display.update()
        join_buttons.clear()
    return True


def main_menu():
    print("Running Main Menu... \n")

    run = True
    global width, height, btn_w, btn_h

    window.fill(green)
    sp_button = Button('Solo play', width // 2 - btn_w // 2, height // 2, (200,200,200), btn_w, btn_h, False)
    server_button = Button('Servers', width // 2 - btn_w // 2, sp_button.rect.bottom + 10, (0, 0, 255), btn_w, btn_h, False)
    help_button = Button('Help', width // 2 - btn_w // 2, server_button.rect.bottom + 10, (200,200,200), btn_w, btn_h, False)
    font = pygame.font.SysFont('arial', 10)
    coming_soon = font.render('Coming soon', 1, black)

    logo = pygame.image.load('big_two_logo.png')
    logo_size = logo.get_rect().size

    fail_connect = False
    server_font = pygame.font.SysFont('arial', btn_h // 4)
    connecting_text = server_font.render('Connecting...', 1, white)
    fail_text = server_font.render('Failed to connect!', 1, red)
    start_time = 0

    while run:
        clock.tick(30)

        window.fill(green)
        sp_button.draw(window)
        window.blit(coming_soon, (width // 2 - coming_soon.get_rect().size[0] // 2, sp_button.rect.bottom - 20))
        server_button.draw(window)
        help_button.draw(window)
        window.blit(coming_soon, (width // 2 - coming_soon.get_rect().size[0] // 2, help_button.rect.bottom - 20))
        draw(logo, width // 2 - logo_size[0] // 2, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if server_button.click(pos):
                    server_button.darken_button()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if server_button.click(pos) and server_button.is_held_down:
                    if not server_menu():
                        start_time = pygame.time.get_ticks()
                        fail_connect = True
                    server_button.lighten_button()
                elif not server_button.click(pos) and server_button.is_held_down:
                    server_button.lighten_button()

        while fail_connect:
            window.blit(fail_text, (server_button.rect.right + 10, server_button.y + btn_h // 2 - fail_text.get_rect().size[1] // 2))
            if pygame.time.get_ticks() - start_time == 1000:
                fail_connect = False
                break
            pygame.display.update()

        pygame.display.update()


while True:
    main_menu()
    log_file = open('log.txt', 'w')
    log_file.write("Client has closed successfully \n")
    log_file.close()
    print("Written to log file!")
    pygame.quit()
    break
