from os import environ

SESSION_CONFIGS = [
    dict(
        name="vers_1",
        display_name="Capstone Activity 1",
        num_demo_participants=1,
        app_sequence=["activity1", "survey"],
        task='transcription',
        attempts_per_puzzle=2,
        retry_delay=3.0,
    ),
    dict(
        name="vers_2",
        display_name="Capstone Activity 2",
        num_demo_participants=1,
        app_sequence=["activity2", "survey"],
        task='matrix',
        attempts_per_puzzle=2,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['is_dropout']
SESSION_FIELDS = ['params']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_TITLE = "Principal-Agent Capstone"
DEMO_PAGE_INTRO_HTML = """
Min Jie Kim (mjk9913) Capstone 
"""

SECRET_KEY = "2015765205890"

