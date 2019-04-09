from questionary import Validator, ValidationError

class IntegerValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter an integer number',
                cursor_position=len(document.text))  # Move cursor to end

class FloatValidator(Validator):
    def validate(self, document):
        try:
            float(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a float number',
                cursor_position=len(document.text))  # Move cursor to end

class StringValidator(Validator):
    def validate(self, document):
        try:
            str(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a string value',
                cursor_position=len(document.text))  # Move cursor to end