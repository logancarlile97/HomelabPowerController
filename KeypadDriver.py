import RPi.GPIO as GPIO
import time
from ConfigReader import ConfigReader
import logging

#Below imports are specific to the Authenticator class
from LcdDriver import LcdDriver
import time

class KeypadDriver:
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

        #Set object defined logger to log for ease of readability and usability in code

        log = self.logger 

        # Holds the values entered on keypad

        entry = '' 

        try:

            # Set all Column pins to output high

            for j in range(len(COL)):
                GPIO.setup(COL[j], GPIO.OUT)
                GPIO.output(COL[j], 1)

            # Set all Row pins to input and pull up to high

            for i in range(len(ROW)):
                GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Loop until a entry is entered by the user

            while True: 

                # Loop through each column pin and set output to low

                for j in range(len(COL)): 
                    GPIO.output(COL[j], 0)

                    # Loop through each row pin and see if its input is low
                    # This will determine not only if a key is pressed but
                    # also what column and row the button press is associated with.

                    for i in range(len(ROW)):
                        if GPIO.input(ROW[i]) == 0:

                            # If the key pressed is a pound then print, return, and clear the entry

                            if KEYS[i][j] == '#':
                                log.info(f'User inputed {entry} via keypad')
                                
                                # Cleanup GPIO pins when program finishes

                                GPIO.cleanup(ROW + COL) 
                                
                                # Return the user entered entry

                                return entry 

                            # If the key pressed is a asterisk then clear entry

                            elif KEYS[i][j] == '*': 
                                log.debug(f'User cleared message')
                                entry = ''
                            
                            # Otherwise add inputted key to entry

                            else: 
                                pressedKey = KEYS[i][j]
                                log.debug(f'New keypress of {pressedKey} detected from user')
                                entry += pressedKey
                                pressedKey = ''

                            # While a key is being held down this will loop

                            while GPIO.input(ROW[i]) == 0: 
                                
                                # Sleep to prevent key bouncing

                                time.sleep(0.002) 
                                pass

                    # Set the column pin to

                    GPIO.output(COL[j], 1)
                    
                    #Delay to prevent busy waiting

                    time.sleep(0.0005) 
                    
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

        #Set object defined logger to log for ease of readability and usability in code

        log = self.logger 

        try:

            # Set all Column pins to output high

            for j in range(len(COL)):
                GPIO.setup(COL[j], GPIO.OUT)
                GPIO.output(COL[j], 1)

            # Set all Row pins to input and pull up to high

            for i in range(len(ROW)):
                GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Loop until a entry is entered by the user

            while True: 
                
                # Loop through each column pin and set output to low

                for j in range(len(COL)): 
                    GPIO.output(COL[j], 0)

                    # Loop through each row pin and see if its input is low
                    # This will determine not only if a key is pressed but
                    # also what column and row the button press is associated with.

                    for i in range(len(ROW)):
                        
                        if GPIO.input(ROW[i]) == 0:
                            pressedKey = KEYS[i][j]
                            
                            # While a key is being held down this will loop

                            while GPIO.input(ROW[i]) == 0: 
                                
                                # Sleep to prevent key bouncing

                                time.sleep(0.002) 
                            return pressedKey

                    # Set the column pin to

                    GPIO.output(COL[j], 1)
                    
                    #Delay to prevent busy waiting

                    time.sleep(0.0005) 

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
        
        #Setup config file

        self.config = ConfigReader('config.ini') 

        #Create and configure logger

        LOG_Format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename = self.config.getLogConfig('logFile'),
                            level = self.config.getLogConfig('logLevel'),
                            format = LOG_Format)
        self.logger = logging.getLogger()
        self.logger.info(f'Authenticator Initialized')

        try:
            
            #Initialize LCD

            self.LCD = LcdDriver()
            
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
        
        #Loop until user enters correct pin or enter exitAuthCode

        while(True): 
            
            #Get current pressed key

            pressedKey = keypad.press() 
            log.debug(f'Newly pressed key: {pressedKey}')

            #If pressedKey is the enter key then begin auth processing
            
            if (pressedKey == '#'): 
                log.info(f'User inputed pin')
                lcd.print('', 'Analysing...')
                time.sleep(1)
                
                #If user inputed exit code then return False

                if(userInput == exitAuthCode): 
                    log.info(f'Authenticator could not validat user')
                    return False
                
                #If user inputed invalid pin

                elif(userInput != pin): 
                    time.sleep(2)
                    log.warning(f'User inputed invalid pin on keypad')
                    lcd.print('',f'Attempt {crntAttempt} of {maxAttempts}')
                    time.sleep(1)
                    
                    #If user has reached maximum attempts

                    if(crntAttempt >= maxAttempts): 
                        log.warning(f'User has reached max attempts, locking out for {lockoutTime} seconds')
                        lcd.print('Locked Out for:', f'{lockoutTime} seconds')
                        time.sleep(lockoutTime)
                        
                        #Reset currnet attempt

                        crntAttempt = 1 
                    lcd.print('','Enter Pin')
                
                #If user inputed correct pin then return True

                elif(userInput == pin): 
                    log.warning(f'Authenticator validated user')
                    return True
                
                #Increment current attempt

                crntAttempt += 1 
                userInput = ''
            
            #If pressedKey is the clear key then clear userInput

            elif (pressedKey == '*'): 
                userInput = ''
                lcd.print('', ' ')
            
            #Otherwise add pressed key to userInput

            else: 
                userInput += pressedKey
                
                #Reset pressed key

                pressedKey = '' 

            #If user says they want to obfuscate their pin

            if(config.getAuthConfig('obfuscatePin') == True): 
                obfuscatedPin = ''
                for x in range(len(userInput)):
                    if(x == len(userInput)-1):
                        obfuscatedPin += userInput[x]
                    else:
                        obfuscatedPin += '*'
                
                #Display obfuscated pin

                lcd.print('Authenticator', obfuscatedPin) 
                
            else:
                lcd.print('Authenticator', userInput)
