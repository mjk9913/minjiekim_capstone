from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    q1 = models.StringField(
        choices = ['Very positive (+2)', 'Positive (+1)', 'Neutral (0)', 'Negative (-1)', 'Very negative (-2)']
    )
    q2 = models.StringField(
        choices = ['Very positive (+2)', 'Positive (+1)', 'Neutral (0)', 'Negative (-1)', 'Very negative (-2)']
    )
    q3 = models.IntegerField(
        choices = [10,20,30,40,50]
    )
    q4 = models.IntegerField(
        choices = [10,20,30,40,50]
    )
    q5 = models.IntegerField(
        choices = [10,20,30,40,50]
    )
    q6 = models.IntegerField(
        choices = [10,20,30,40,50]
    )
    q7 = models.StringField(
        choices = ['Contingent contract', 'Unconditional contract', 'Coin toss']
    )
    q8 = models.StringField(
        choices = ['Yes', 'No']
    )
    q9 = models.IntegerField(
    )
    q10 = models.StringField(
        choices = ['Male', 'Female', 'Other']
    )
    q11 = models.StringField(
        widget=widgets.RadioSelect,
        choices = ['White', 'Black or African American', 'Asian', 'American Indian or Alaska Native', 'Middle Eastern or North African', 'Other']
    )
    q12 = models.StringField(
        choices = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'U.S. territory (e.g., Puerto Rico)', 'Some other country']
    )
    q13 = models.StringField(
        choices = ['Less than high school', 'High school graduate', 'Some college', '2-year degree (Associate’s)', '4-year degree (Bachelor’s)', 'Graduate or professional degree']
    )
    q14 = models.StringField(
        choices = ['Less than $10,000', '$10,000 to $19,999', '$20,000 to $29,999', '$30,000 to $39,999', '$40,000 to $49,999', '$50,000 to $59,999', '$60,000 to $69,999', '$70,000 to $79,999', '$80,000 to $89,999', '$90,000 to $99,999', '$100,000 to $149,999', '$150,000 or more']
    )
    q15 = models.StringField(
        choices = ['Full-time', 'Part-time', 'Unemployed', 'Unemployed temporarily', 'Unemployed long-term']
    )
    q16 = models.StringField(
        choices = ['Public', 'Private', 'Self-employed']
    )
    q17 = models.StringField(blank=True)
    mturk_code = models.LongStringField()


# PAGES
class Survey(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12', 'q13', 'q14','q15','q16','q17']
    pass

class Mturk(Page):
    form_model = 'player'
    form_fields = ['mturk_code']


page_sequence = [Survey, Mturk]
