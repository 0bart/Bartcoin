from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length

class GenerateForm(FlaskForm):
    generate = SubmitField('Generate!')

class CheckWalletForm(FlaskForm):
    wallet_add = StringField('Wallet address..', [DataRequired(), Length(min=33, max=33)])
    submit = SubmitField('Search!')

class NewTransactionForm(FlaskForm):
    wallet_add = StringField('Sender wallet address..', [DataRequired(), Length(min=33, max=33)])
    recipient = StringField('Recipient wallet address..', [DataRequired(), Length(min=33, max=33)])
    amount = FloatField('Amount..', [DataRequired()])
    sign = StringField('Sign..', [DataRequired(), Length(min=66, max=66)])
    submit = SubmitField('Send!')