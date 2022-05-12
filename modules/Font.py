from pathlib import Path
from re import match
from re import compile as re_compile

from modules.Debug import log
from modules.TitleCard import TitleCard
import modules.preferences as global_preferences

class Font:
    """
    This class describes a font and all of its configurable attributes. Notably,
    it's color, size, file, replacements, case function, vertical offset, and 
    interline spacing.
    """
    
    """Compiled regex to identify percentage values"""
    _PERCENT_REGEX = re_compile(r'^-?\d+\.?\d*%$')
    _PERCENT_REGEX_POSITIVE = re_compile(r'^\d+\.?\d*%$')

    __slots__ = ('valid', '__yaml', '__card_class','__font_map','__series_info',
                 '__validator', '__validate', 'color', 'size', 'file',
                 'replacements', 'case_name', 'case', 'vertical_shift',
                 'interline_spacing', 'kerning', 'stroke_width')
    

    def __init__(self, yaml, font_map: dict, card_class: 'CardType',
                 series_info: 'SeriesInfo') -> None:
        """
        Constructs a new instance of a Font for the given YAML, CardType, and
        series.
        
        :param      yaml:           'font' dictionary from a series YAML file.
        :type       yaml:           Dict or str. If str, must be a key of
                                    font_map.
        :param      font_map:       Map of font labels to custom font
                                    dictionaries.
        :param      card_class:     CardType class to use values from.
        :param      series_info:    Associated SeriesInfo (for logging).
        """

        # Assume object is valid to start with
        self.valid = True

        # If the given value is a key of the font map, use those values instead
        if isinstance(yaml, str) and yaml in font_map:
            yaml = font_map[yaml]
        
        # If font YAML (either from map or directly) is not a dictionary, bad!
        if not isinstance(yaml, dict):
            log.error(f'Invalid font for series "{series_info}"')
            self.valid = False
            yaml = {}

        # Store arguments
        self.__yaml = yaml
        self.__card_class = card_class
        self.__font_map = font_map
        self.__series_info = series_info

        # Use the global FontValidator object
        self.__validator = global_preferences.fv
        
        # Generic font attributes
        self.set_default()
        
        # Parse YAML, update validity
        self.__parse_attributes()

        
    def __repr__(self) -> str:
        """Returns an unambiguous string representation of the object."""
        
        return f'<CustomFont for series "{self.__series_info}">'


    def __parse_attributes(self) -> None:
        """Parse this object's YAML and update the validity and attributes."""

        # Whether to validate for this font
        if (value := self.__yaml.get('validate')) != None:
            self.__validate = bool(value)

        # Font case
        if (value := self.__yaml.get('case', '').lower()) != '':
            if value not in self.__card_class.CASE_FUNCTIONS:
                log.error(f'Font case "{value}" of series {self.__series_info} '
                          f'is invalid')
                self.valid = False
            else:
                self.case_name = value
                self.case = self.__card_class.CASE_FUNCTIONS[value]

        # Font color
        if (value := self.__yaml.get('color')) != None:
            if not bool(match('^#[a-fA-F0-9]{6}$', value)):
                log.error(f'Font color "{value}" of series {self.__series_info}'
                          f' is invalid - specify as "#xxxxxx"')
                self.valid = False
            else:
                self.color = value

        # Font file
        if (value := self.__yaml.get('file')) != None:
            if not Path(value).exists():
                log.error(f'Font file "{value}" of series {self.__series_info} '
                          f'not found')
                self.valid = False
            else:
                self.file = str(Path(value).resolve())
                self.replacements = {} # Reset for manually specified font

        # Font replacements
        if (value := self.__yaml.get('replacements')) != None:
            if any(len(key) != 1 for key in value.keys()):
                log.error(f'Font replacements of series {self.__series_info} is'
                          f' invalid - must only be 1 character')
                self.valid = False
            elif not all(isinstance(repl, str) for _, repl in value.items()):
                log.error(f'Font replacements of series {self.__series_info} is'
                          f' invalid - can only substitute strings')
                self.valid = False
            else:
                self.replacements = value

        # Font Size
        if (value := self.__yaml.get('size')) != None:
            if not bool(self._PERCENT_REGEX_POSITIVE.match(value)):
                log.error(f'Font size "{value}" of series {self.__series_info} '
                          f'is invalid - specify as "x%"')
                self.valid = False
            else:
                self.size = float(value[:-1]) / 100.0

        # Vertical shift
        if (value := self.__yaml.get('vertical_shift')) != None:
            if not isinstance(value, int):
                log.error(f'Font vertical shift "{value}" of series '
                          f'{self.__series_info} is invalid - must be integer.')
                self.valid = False
            else:
                self.vertical_shift = value

        # Interline spacing
        if (value := self.__yaml.get('interline_spacing')) != None:
            if not isinstance(value, int):
                log.error(f'Font interline spacing "{value}" of series '
                          f'{self.__series_info} is invalid - must be integer.')
                self.valid = False
            else:
                self.interline_spacing = value
                
        # Kerning
        if (value := self.__yaml.get('kerning')) != None:
            if not bool(self._PERCENT_REGEX.match(value)):
                log.error(f'Font kerning "{value}" of series '
                          f'{self.__series_info} is invalid - specify as "x%"')
                self.valid = False
            else:
                self.kerning = float(value[:-1]) / 100.0

        # Stroke width
        if (value := self.__yaml.get('stroke_width')) != None:
            if not bool(self._PERCENT_REGEX_POSITIVE.match(value)):
                log.error(f'Font stroke width "{value}" of series '
                          f'{self.__series_info} is invalid - specify as "x%"')
                self.valid = False
            else:
                self.stroke_width = float(value[:-1]) / 100.0


    def set_default(self) -> None:
        """Reset this object's attributes to its default values."""

        # Whether to validate for this font
        self.__validate = global_preferences.pp.validate_fonts

        # Title card characteristics
        self.color = self.__card_class.TITLE_COLOR
        self.size = 1.0
        self.file = self.__card_class.TITLE_FONT
        self.replacements = self.__card_class.FONT_REPLACEMENTS
        self.case_name = self.__card_class.DEFAULT_FONT_CASE
        self.case = self.__card_class.CASE_FUNCTIONS[self.case_name]
        self.vertical_shift = 0
        self.interline_spacing = 0
        self.kerning = 1.0
        self.stroke_width = 1.0


    def get_attributes(self) -> dict:
        """
        Return a dictionary of attributes for this font to be unpacked.
        
        :returns:   Dictionary of attributes.
        """

        return {
            'title_color': self.color,
            'font_size': self.size,
            'font': self.file,
            'vertical_shift': self.vertical_shift,
            'interline_spacing': self.interline_spacing,
            'kerning': self.kerning,
            'stroke_width': self.stroke_width,
        }


    def validate_title(self, title: 'Title') -> bool:
        """
        Return whether all the characters of the given Title are valid for this
        font. This uses the global FontValidator object, and always returns True
        if validation is not enabled.
        
        :param      title:  The Title being validated.
        
        :returns:   True if all the characters of the given Title are contained
                    within this font, False otherwise.
        """

        # Validate title against this font
        validity = self.__validator.validate_title(self.file, title)

        # If validation isn't enabled, ignore result and return True
        return validity if self.__validate else True

        