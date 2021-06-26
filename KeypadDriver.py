import RPi.GPIO as GPIO
import time
from configReader import configReader
import logging

class KeypadDriver():
    """
    The driver for a keypad plugged into the raspberry pi gpio pins
    """

    def __init__(self):
        self.config = configReader('config.ini')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Key layout on keypad
        self.KEYS = config.getKeypadConfig('keypadLayout')

        # Set the GPIO pins for columns and rows,
        # make sure they are in the right order or keys will be backwards
        self.ROW = config.getKeypadConfig('rowPins')
        self.COL = config.getKeypadConfig('columnPins')

        #Create and configure logger
        LOG_Format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename = 'test.log',
                            level = logging.DEBUG,
                            format = LOG_Format)

        self.logger = logging.getLogger()

        #Log the set pins and keymap for keypad, this is in the constructor method so it will not run every time message is called
        self.logger.debug(f'Keypad keymap has been inputed as {self.KEYS}')
        self.logger.debug(f'Keypad row pins, in order of row number, are set as {self.ROW}')
        self.logger.debug(f'Keypad column pins, in order of column number, are set as {self.COL}')

    def message(self):
        """
        Returns user input from external keypad. Will loop until user presses the enter key of '#'
        """
        #Set keymap and assosiated pins for column and row
        ROW = self.ROW
        COL = self.COL
        KEYS = self.KEYS

        log = self.logger() #Set object defined logger to log for ease of readability and usability in code

        entry = '' # Holds the values entered on keypad

        try:

            # Set all Column pins to output high
            for j in range(len(COL)):
                GPIO.setup(COL[j], GPIO.OUT)
                GPIO.output(COL[j], 1)

            # Set all Row pins to input and pull up to high
            for i in range(len(ROW)):
                GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

            
            while True: # Loop until a entry is entered by the user

                
                for j in range(len(COL)): # Loop through each column pin and set output to low
                    GPIO.output(COL[j], 0)

                    # Loop through each row pin and see if its input is low
                    # This will determine not only if a key is pressed but
                    # also what column and row the button press is associated with.
                    for i in range(len(ROW)):
                        if GPIO.input(ROW[i]) == 0:

                            # If the key pressed is a pound then print, return, and clear the entry
                            if KEYS[i][j] == '#':
                                log.info(f'User inputed {entry} via keypad')
                                GPIO.cleanup(ROW + COL) # Cleanup GPIO pins when program finishes
                                return entry # Return the user entered entry

                            
                            elif KEYS[i][j] == '*': # If the key pressed is a asterisk then clear entry
                                log.debug(f'User cleared message')
                                entry = ''
                            
                            else: # Otherwise add inputted key to entry
                                pressedKey = KEYS[i][j]
                                log.debug(f'New keypress of {pressedKey} detected from user')
                                entry += pressedKey
                                pressedKey = ''

                            
                            while GPIO.input(ROW[i]) == 0: # While a key is being held down this will loop
                                time.sleep(0.2) # Sleep to prevent key bouncing
                                pass

                    # Set the column pin to
                    GPIO.output(COL[j], 1)

        # Print any other errors to terminal
        except Exception as e:
            log.error(f'KeypadDriver ran into an unexpected error: \n\t{e}')
            print('Keypad test ran into an error')
            print('Exception: ' + str(e))
            GPIO.cleanup(ROW + COL)
