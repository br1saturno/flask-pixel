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

color_moods = [ ("earthy", "Earthy"), ("coastal", "Coastal"), ("classic", "Classic"), ("traditional", "Traditional"),
               ("serene", "Serene"), ("sophisticated", "Sophisticated"), ("ultra_modern", "Ultra-Modern"),
               ("energetic", "Energetic"), ("fun", "Fun"), ("eclectic", "Eclectic"), ]

room_types = [ ("entrance", "Residential - Entrance"), ("living", "Residential - Living Room"),
               ("kitchen", "Residential - Kitchen"), ("bedroom", "Residential - Bedroom"),
               ("bathroom", "Residential - Bathroom"), ("res_office", "Residential - Office"),
               ("terrace", "Residential - Terrace"), ("hallway", "Residential - Hallway"),
               ("com_office", "Commercial - Office"), ("coworking", "Commercial - Coworking"),
               ("coffee_shop", "Commercial - Coffee Shop"), ("store", "Commercial - Store"),
               ("restaurant", "Commercial - Restaurant"), ("rest_patio", "Commercial - Restaurant Patio"),
               ("hotel_lobby", "Commercial - Hotel Lobby"), ("hotel_room", "Commercial - Hotel Room"),
               ("hotel_bath", "Commercial - Hotel Bathroom"), ]

colors_combs = [("sage green", "beige", "cream white"), ("blue", "tan", "crisp white"),
                ("blue and white", "Calming neutrals as supportive colors"), ("burgundy", "deep green", "brown"),
                ("white", "beige", "light green"), ("gray", "white", "blue"), ("black", "white", "gray"),
                ("coral", "teal", "beige"), ("pink", "green", "gray"), ("blue", "red", "brown")]

color_moods_dict = {color_moods[n][0]: colors_combs[n] for n in range(len(colors_combs))}

aspect_ratio = [("1", "4:3"), ("2", "3:4"), ("3", "1:1"), ("4", "16:9"), ("5", "9:16")]

aspect_ratio_low = {
    "1": (512, 384),
    "2": (384, 512),
    "3": (512, 512),
    "4": (1024, 576),
    "5": (576, 1024),
}



