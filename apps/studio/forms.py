from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField, IntegerRangeField
from wtforms.validators import DataRequired, Length, InputRequired, Email

WTF_CSRF_SECRET_KEY = 'HKGUPIK34456ljfhPO&^$'

styles = [ ("art_nouveau", "Art Nouveau"), ("art_deco", "Art Deco"), ("arts_crafts", "Arts & Crafts"),
           ("arabian", "Arabian"), ("asian", "Asian"), ("bauhaus", "Bauhaus"), ("bohemian", "Bohemian"),
           ("california_chic", "California Chic"), ("coastal", "Coastal"), ("contemporary", "Contemporary"),
           ("country_house", "Country House"), ("eclectic", "Eclectic"), ("french_country", "French Country"),
           ("hollywood_reg", "Hollywood regency"), ("industrial", "Industrial"), ("japandi", "Japandi"),
           ("mid_modern", "Midcentury modern"), ("minimal", "Minimal"), ("med", "Mediterranean"), ("modern", "Modern"),
           ("moroccan", "Moroccan"), ("parisian", "Parisian"), ("rustic", "Rustic"), ("shabby_chic", "Shabby Chic"),
           ("southwest", "Southwestern"), ("scandi", "Scandinavian"), ("traditional", "Traditional"),
           ("transitional", "Transitional"), ("tropical", "Tropical"), ("tribal", "Tribal"), ]

color_feels = [ ("earthy", "Earthy"), ("coastal", "Coastal"), ("classic", "Classic"), ("traditional", "Traditional"),
               ("serene", "Serene"), ("sophisticated", "Sophisticated"), ("ultra_modern", "Ultra-Modern"),
               ("energetic", "Energetic"), ("fun", "Fun"), ("eclectic", "Eclectic"), ]

room_types = [ ("entrance", " Residential - Entrance"), ("living", " Residential - Living Room"),
               ("kitchen", " Residential - Kitchen"), ("bedroom", " Residential - Bedroom"),
               ("bathroom", " Residential - Bathroom"), ("res_office", " Residential - Office"),
               ("terrace", " Residential - Terrace"), ("hallway", " Residential - Hallway"),
               ("com_office", " Commercial - Office"), ("coworking", " Commercial - Coworking"),
               ("coffee_shop", " Commercial - Coffee Shop"), ("store", " Commercial - Store"),
               ("restaurant", " Commercial - Restaurant"), ("rest_patio", " Commercial - Restaurant Patio"),
               ("hotel_lobby", " Commercial - Hotel Lobby"), ("hotel_room", " Commercial - Hotel Room"),
               ("hotel_bath", " Commercial - Hotel Bathroom"), ]


class StudioForm(FlaskForm):
    style = SelectField(u'Style', choices=styles, id='style', validators=[DataRequired()])
    color_feel = SelectField(u'Color feel', choices=color_feels, id='color_feel', validators=[DataRequired()])
    room_type = SelectField(u'Type of room', choices=room_types, id='room_type', validators=[DataRequired()])
    samples = IntegerRangeField(u'Number of samples')
    submit = SubmitField(label='Render')

