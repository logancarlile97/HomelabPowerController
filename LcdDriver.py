import adafruit_character_lcd.character_lcd as characterLCD
import board
import digitalio
import time
import logging

class LcdDriver():
    """
    A class to handle the lcd
    """
    def __init__(self):
        # Assign each lcd pin to GPIO
        lcd_rs = digitalio.DigitalInOut(board.D17)  # GPIO 17 pin 11
        lcd_en = digitalio.DigitalInOut(board.D27)  # GPIO 27 pin 13
        lcd_d4 = digitalio.DigitalInOut(board.D22)  # GPIO 22 pin 15
        lcd_d5 = digitalio.DigitalInOut(board.D10)  # GPIO 10 pin 19
        lcd_d6 = digitalio.DigitalInOut(board.D9)  # GPIO 9 pin 21
        lcd_d7 = digitalio.DigitalInOut(board.D11)  # GPIO 11 pin 23
        lcd_columns = 16
        lcd_rows = 2

        self.lcd = characterLCD.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns,
                                                   lcd_rows)
        #Create and configure logger
        LOG_Format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename = 'test.log',
                            level = logging.INFO,
                            format = LOG_Format)

        self.logger = logging.getLogger()

    def print(self, top, bottom):
        """
        Prints top and bottom to the top and bottom of the lcd respectivly
        """
        log = self.logger

        log.debug(f'lcd top message: {top}')
        log.debug(f'lcd bottom message: {bottom}')
        
        if len(top) == 0:
            adjTop = top
        else:
            adjTop = top.ljust(16)

        if len(bottom) == 0:
            adjBottom = bottom
        else:
            adjBottom = "\n" + bottom.ljust(16)

        log.debug(f'lcd message printed')
        self.lcd.message = adjTop + adjBottom
        log.info(f'Current lcd message: \n{adjTop+adjBottom}')

    def clear(self):
        """
        Clears all text on the lcd
        """
        log = self.logger

        
        self.lcd.clear()
        log.info(f'LCD has been cleared')


lcd = LcdDriver()
