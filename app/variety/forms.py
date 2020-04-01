from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Email


class VarietyForm(FlaskForm):

    variety_name = StringField('Name', validators=[DataRequired()])
    variety_type = SelectField('Type',
                               validators=[DataRequired()],
                               choices=[("Nature", "Nature"),
                                        ("Mutans", "Mutans"),
                                        ("Transgenesis", "Transgenesis"),
                                        ("Other", "Other")],
                               coerce=str)
    geographic = StringField('Geographic', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    province = StringField('Province', validators=[DataRequired()])
    affiliation = StringField('Affiliation', validators=[DataRequired()])
    flower_color = StringField('Flower Color')
    leaf_color = StringField('Leaf Color')
    protein_content = StringField('Protein Content')
    starch_content = StringField('Starch Content')
    salt = SelectField('Salt',
                       choices=[("", "---select---"), ("Unkown", "Unkown"),
                                ("No", "No"), ("Low", "Low"),
                                ("Medium", "Medium"), ("High", "High")],
                       coerce=str)
    high_temperature = SelectField('High Temperature',
                                   choices=[("", "---select---"),
                                            ("Unkown", "Unkown"), ("No", "No"),
                                            ("Low", "Low"),
                                            ("Medium", "Medium"),
                                            ("High", "High")],
                                   coerce=str)
    low_temperature = SelectField('Low Temperature',
                                  choices=[("", "---select---"),
                                           ("Unkown", "Unkown"), ("No", "No"),
                                           ("Low", "Low"),
                                           ("Medium", "Medium"),
                                           ("High", "High")],
                                  coerce=str)
    sheath_blight = StringField('Sheath Blight')
    fusarium = StringField('Fusarium')
    total_erosion = StringField('Total Erosion')
    powdery_mildew = StringField('Powdery Mildew')
    leaf_rust = StringField('Leaf Rust')
    leaf_blight = StringField('Leaf Blight')
    stripe_rust = StringField('Stripe Rust')
    spinal_rust = StringField('Spinal Rust')
    smut = StringField('Smut')

    def __init__(self, *args, **kwargs):
        super(VarietyForm, self).__init__(*args, **kwargs)
        self.user = None


class VarietyCommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(VarietyCommentForm, self).__init__(*args, **kwargs)
        self.user = None
