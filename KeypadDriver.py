import RPi.GPIO as GPIO
import time
from ConfigReader import ConfigReader
import logging

#Below imports are specific to the Authenticator class
from LcdDriver import LcdDriver
import time

class KeypadDriver():
    """
    The driver for a keypad plugged into the raspberry pi gpio pins
    """

    def __init__(self):
        self.config = ConfigReader('config.ini')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Key layout on keypad
        self.KEYS = self.config.getKeypadConfig('keypadLayout')

        # Set the GPIO pins for columns and rows,
        # make sure they are in the right order or keys will be backwards
        self.ROW = self.config.getKeypadConfig('rowPins')
        self.COL = self.config.getKeypadConfig('columnPins')

        #Create and configure logger
        LOG_Format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename = self.config.getLogConfig('logFile'),
                            level = self.config.getLogConfig('logLevel'),
                            format = LOG_Format)

        self.logger = logging.getLogger()

        #Log the set pins and keymap for keypad, this is in the constructor method so it will not run every time message is called
        self.logger.debug(f'Keypad keymap has been inputed as {self.KEYS}')
        self.logger.debug(f'Keypad row pins, in order of row number, are set as {self.ROW}')
        self.logger.debug(f'Keypad column pins, in order of column number, are set as {self.COL}')

    def input(self):
        """
        Returns user input from external keypad. Will loop until user presses the enter key of '#'
        """
        #Set keymap and assosiated pins for column and row
        ROW = self.ROW
        COL = self.COL
        KEYS = self.KEYS

        log = self.logger #Set object defined logger to log for ease of readability and usability in code

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

    def press(self):
        """
        Returns each pressed key, does not wait until user presses enter
        """
        #Set keymap and assosiated pins for column and row
        ROW = self.ROW
        COL = self.COL
        KEYS = self.KEYS

        log = self.logger #Set object defined logger to log for ease of readability and usability in code

        try:

            # Set all Column pins to output high
            for j in range(len(COL)):
                GPIO.setup(COL[j], GPIO.OUT)
                GPIO.output(COL[j], 1)

            # Set all Row pins to input and pull up to high
            for i in range(len(ROW)):
                GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

            
            while True: # Loop until a entry is entered by the user
                time.sleep(0.001) #Delay to prevent over utilization of cpu resources
                
                for j in range(len(COL)): # Loop through each column pin and set output to low
                    GPIO.output(COL[j], 0)

                    # Loop through each row pin and see if its input is low
                    # This will determine not only if a key is pressed but
                    # also what column and row the button press is associated with.
                    for i in range(len(ROW)):
                        
                        if GPIO.input(ROW[i]) == 0:
                            pressedKey = KEYS[i][j]
                            while GPIO.input(ROW[i]) == 0: # While a key is being held down this will loop
                                time.sleep(0.2) # Sleep to prevent key bouncing
                                pass
                            return pressedKey

                    # Set the column pin to
                    GPIO.output(COL[j], 1)

        # Print any other errors to terminal
        except Exception as e:
            log.error(f'KeypadDriver ran into an unexpected error: \n\t{e}')
            print('Keypad test ran into an error')
            print('Exception: ' + str(e))
            GPIO.cleanup(ROW + COL)


class Authenticator:
    """
    Works in collaboration with KeypadDriver and LcdDriver to ask user for predefined pin.
    """
    
    def __init__(self):
        self.config = ConfigReader('config.ini') #Setup config file

        #Create and configure logger
        LOG_Format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename = self.config.getLogConfig('logFile'),
                            level = self.config.getLogConfig('logLevel'),
                            format = LOG_Format)
        self.logger = logging.getLogger()
        self.logger.info(f'Authenticator Initialized')

        try:
            self.LCD = LcdDriver() #Initialize LCD
        except Exception as e:
            self.logger.critical(f'Authenticator could not initialize LcdDriver')
            self.logger.critical(f'Exception rasied: \n\t{e}')
            print('Could not load lcdDriver')
        
        try:
            self.Keypad = KeypadDriver()
        except Exception as e:
            self.logger.critical(f'Authenticator could not initialize Keypad Driver')
            self.logger.critical(f'Exception rasied: \n\t{e}')
            print('Could not load Keypad Driver')

    def verified(self):
        """
        Returns whether or not user could be verified via keypad
        """
        
        config = self.config
        log = self.logger

        maxAttempts = config.getAuthConfig('maxAttempts')
        lockoutTime = config.getAuthConfig('lockoutTime')
        pin = config.getAuthConfig('pin')
        exitAuthCode = config.getAuthConfig('exitAuthenticatorCode')
        crntAttempt = 1
        userInput = ''

        lcd = self.LCD 
        keypad = self.Keypad

        log.debug(f'Nessecary Authenticator variables finished setup')
        
        lcd.print('Authenticator', 'Enter Pin')

        log.debug('Entered authenticator loop')
        while(True): #Loop until user enters correct pin or enter exitAuthCode
            pressedKey = keypad.press() #Get current pressed key
            log.debug(f'Newly pressed key: {pressedKey}')

            if (pressedKey == '#'): #If pressedKey is the enter key then begin auth processing
                log.info(f'User inputed pin')
                lcd.print('', 'Analysing...')
                time.sleep(1)
                
                if(userInput == exitAuthCode): #If user inputed exit code then return False
                    log.info(f'Authenticator could not validat user')
                    return False
                elif(userInput != pin): #If user inputed invalid pin
                    time.sleep(2)
                    log.warning(f'User inputed invalid pin on keypad')
                    lcd.print('',f'Attempt {crntAttempt} of {maxAttempts}')
                    time.sleep(1)
                    if(crntAttempt >= maxAttempts): #If user has reached maximum attempts
                        log.warning(f'User has reached max attempts, locking out for {lockoutTime} seconds')
                        lcd.print('Locked Out for:', f'{lockoutTime} seconds')
                        time.sleep(lockoutTime)
                        crntAttempt = 1 #Reset currnet attempt
                    lcd.print('','Enter Pin')
                elif(userInput == pin): #If user inputed correct pin then return True
                    log.warning(f'Authenticator validated user')
                    return True
                crntAttempt += 1 #Increment current attempt
                userInput = ''
            elif (pressedKey == '*'): #If pressedKey is the clear key then clear userInput
                userInput = ''
                lcd.print('', ' ')
            else: #Otherwise add pressed key to userInput
                userInput += pressedKey
                pressedKey = '' #Reset pressed key

            lcd.print('Authenticator', userInput) #Display new userInput on screen so user can see pin


