import time, csv, random

from otree import settings
from otree.api import *

from .image_utils import encode_image

doc = """
Capstone: Activity 1
"""

class Constants(BaseConstants):
    name_in_url = "activity1"
    players_per_group = None
    num_rounds = 1
    used_captcha = models.VarsDict({})
    instructions_template = __name__ + "/instructions.html"
    captcha_length = 3
    employer_human = random.choice([True, False])
    z = 3
    x = 0.5
    with open('activity1/captcha_names.csv', encoding="utf-8-sig") as f:
        c_options = list(csv.DictReader(f))
    csv_num = len(c_options)

class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    session = subsession.session
    defaults = dict(
        retry_delay=1.0, puzzle_delay=1.0, attempts_per_puzzle=1, max_iterations=None
    )
    session.params = {}
    for param in defaults:
        session.params[param] = session.config.get(param, defaults[param])

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    iteration = models.IntegerField(initial=0)
    num_trials = models.IntegerField(initial=0)
    num_correct = models.IntegerField(initial=0)
    num_failed = models.IntegerField(initial=0)
    captchas_done = models.VarsDict()
    curr_image = models.StringField()
    curr_captcha = models.StringField()
    num_rounds = models.IntegerField(initial=0)

    contingent_captchas = models.IntegerField(
        choices = [0,10,20,30,40,50]
    )
    unconditional_captchas = models.IntegerField(
        choices = [0,10,20,30,40,50]
    )
    coin_contingent_captchas = models.IntegerField(
        choices = [0,10,20,30,40,50]
    )
    coin_unconditional_captchas = models.IntegerField(
        choices = [0,10,20,30,40,50]
    )
    captcha_option = models.IntegerField(initial=0)
    final_pay = models.IntegerField(initial=Constants.z)



# puzzle-specific stuff


class Puzzle(ExtraModel):
    """A model to keep record of all generated puzzles"""

    player = models.Link(Player)
    iteration = models.IntegerField(initial=0)
    attempts = models.IntegerField(initial=0)
    timestamp = models.FloatField(initial=0)
    text = models.LongStringField()
    solution = models.LongStringField()
    response = models.LongStringField()
    response_timestamp = models.FloatField()
    is_correct = models.BooleanField()
    curr_image = models.LongStringField()

def set_curr(player: Player):
    randomized_question = random.choice(Constants.c_options)
    if len(player.captchas_done) == Constants.csv_num:
        player.captchas_done = {}
    while randomized_question['graphics_name'] in player.captchas_done:
        randomized_question = random.sample(Constants.c_options, len(Constants.c_options))
    player.captchas_done[randomized_question['graphics_name']] = True
    player.curr_captcha = randomized_question['graphics_name']
    image_path = 'static/quiz/{}.png'.format(randomized_question['solution'])
    player.curr_image = image_path

def generate_puzzle(player: Player) -> Puzzle:
    """Create new puzzle for a player"""
    if player.iteration !=0:
        set_curr(player)
    fields = {'solution': player.curr_captcha, 'curr_image': player.curr_image} 
    player.iteration += 1
    return Puzzle.create(
        player=player, iteration=player.iteration, timestamp=time.time(), **fields
    )

def is_correct(response, puzzle):
    return puzzle.solution.lower() == response.lower()

def get_current_puzzle(player):
    puzzles = Puzzle.filter(player=player, iteration=player.iteration)
    if puzzles:
        [puzzle] = puzzles
        return puzzle


def encode_puzzle(puzzle: Puzzle, player: Player):
    """Create data describing puzzle to send to client"""
    # generate image for the puzzle
    image_path = '/static/quiz/{}.png'.format(puzzle.solution)
    player.curr_image = image_path
    return dict(image=image_path)


def get_progress(player: Player):
    """Return current player progress"""
    return dict(
        num_trials=player.num_trials,
        num_correct=player.num_correct,
        num_incorrect=player.num_failed,
        iteration=player.iteration,
        curr_image = player.curr_image
    )


def play_game(player: Player, message: dict):
    """Main game workflow
    Implemented as reactive scheme: receive message from vrowser, react, respond.

    Generic game workflow, from server point of view:
    - receive: {'type': 'load'} -- empty message means page loaded
    - check if it's game start or page refresh midgame
    - respond: {'type': 'status', 'progress': ...}
    - respond: {'type': 'status', 'progress': ..., 'puzzle': data} -- in case of midgame page reload

    - receive: {'type': 'next'} -- request for a next/first puzzle
    - generate new puzzle
    - respond: {'type': 'puzzle', 'puzzle': data}

    - receive: {'type': 'answer', 'answer': ...} -- user answered the puzzle
    - check if the answer is correct
    - respond: {'type': 'feedback', 'is_correct': true|false, 'retries_left': ...} -- feedback to the answer

    If allowed by config `attempts_pre_puzzle`, client can send more 'answer' messages
    When done solving, client should explicitely request next puzzle by sending 'next' message

    Field 'progress' is added to all server responses to indicate it on page.

    To indicate max_iteration exhausted in response to 'next' server returns 'status' message with iterations_left=0
    """
    session = player.session
    my_id = player.id_in_group
    params = session.params
    now = time.time()
    # the current puzzle or none
    current = get_current_puzzle(player)

    message_type = message['type']
    # page loaded
    if message_type == 'load':
        p = get_progress(player)
        if current:
            return {
                my_id: dict(type='status', progress=p, puzzle=encode_puzzle(current, player))
            }
        else:
            return {my_id: dict(type='status', progress=p)}

    if message_type == "cheat" and settings.DEBUG:
        return {my_id: dict(type='solution', solution=current.solution)}

    # client requested new puzzle
    if message_type == "next":
        if current is not None:
            if current.response is None:
                raise RuntimeError("trying to skip over unsolved puzzle")
            if now < current.timestamp + params["puzzle_delay"]:
                raise RuntimeError("retrying too fast")
            if current.iteration == player.num_rounds:
                return {
                    my_id: dict(
                        type='status', progress=get_progress(player), iterations_left=0
                    )
                }

        # generate new puzzle
        z = generate_puzzle(player)
        p = get_progress(player)
        return {my_id: dict(type='puzzle', puzzle=encode_puzzle(z, player), progress=p)}

    # client gives an answer to current puzzle
    if message_type == "answer":
        if current is None:
            raise RuntimeError("trying to answer no puzzle")

        if current.response is not None:  # it's a retry
            if current.attempts >= params["attempts_per_puzzle"]:
                raise RuntimeError("no more attempts allowed")
            if now < current.response_timestamp + params["retry_delay"]:
                raise RuntimeError("retrying too fast")

            # undo last updation of player progress
            player.num_trials -= 1
            if current.is_correct:
                player.num_correct -= 1
            else:
                player.num_failed -= 1

        # check answer
        answer = message["answer"]

        if answer == "" or answer is None:
            raise ValueError("bogus answer")

        current.response = answer
        current.is_correct = is_correct(answer, current)
        current.response_timestamp = now
        current.attempts += 1

        # update player progress
        if current.is_correct:
            player.num_correct += 1
        else:
            player.num_failed += 1
        player.num_trials += 1

        retries_left = params["attempts_per_puzzle"] - current.attempts
        p = get_progress(player)
        return {
            my_id: dict(
                type='feedback',
                is_correct=current.is_correct,
                retries_left=retries_left,
                progress=p,
            )
        }

    raise RuntimeError("unrecognized message from client")

class Instructions(Page):
    form_model = 'player'
    form_fields = ['contingent_captchas', 'unconditional_captchas', 'coin_contingent_captchas', 'coin_unconditional_captchas']
    @staticmethod
    def is_displayed(player: Player):
        topic_switch = [1]
        #if player.round_number in topic_switch:
        #    return player.round_number == topic_switch
        return player.round_number in topic_switch

    @staticmethod
    def vars_for_template(player: Player):
        compensation = random.choice([True, False])
        return dict(
            compensation= compensation,
            employer = Constants.employer_human,
            captcha_option = Player.captcha_option,
            image_path1= 'quiz/human.png',
            image_path2 = 'quiz/bot.png'
        )
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.captcha_option = random.choice([1,2,3,4])
        for p in player.in_all_rounds():
            if player.captcha_option == 1:
                p.num_rounds = player.contingent_captchas
            elif player.captcha_option == 2:
                p.num_rounds = player.unconditional_captchas
            elif player.captcha_option == 3:
                p.num_rounds = player.coin_contingent_captchas
            elif player.captcha_option == 4:
                p.num_rounds = player.coin_unconditional_captchas
            print(p.num_rounds)

class Game(Page):
    #timeout_seconds = 60
    @staticmethod
    def is_displayed(player):
        return player.num_rounds > 0

    live_method = play_game

    @staticmethod
    def js_vars(player: Player):
        return dict(params=player.session.params)

    @staticmethod
    def vars_for_template(player: Player):
        set_curr(player)
        return dict(DEBUG=settings.DEBUG,
                    image_path = player.curr_image,
                    total_num = player.num_rounds
                    )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not timeout_happened and not player.num_rounds:
            raise RuntimeError("malicious page submission")


class Results(Page):
    def vars_for_template(player: Player):
        if player.captcha_option == 1:
            if player.contingent_captchas < 30:
                player.payoff = 0
        if player.captcha_option == 3:
            if player.coin_contingent_captchas < 30:
                player.payoff = 0
        return dict(
            employer = Constants.employer_human,
            captcha_option = player.captcha_option,
        )



page_sequence = [Instructions, Game, Results]
