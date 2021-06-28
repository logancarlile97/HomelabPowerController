from KeypadDriver import KeypadDriver, Authenticator
from ConfigReader import ConfigReader
import logging
from LcdDriver import LcdDriver
import time

class HLPC:
    """
    Class to allow for all frontend operations of the HLPC program.
    """
    
    def __init__(self):
        self.config = ConfigReader('config.ini')

        #Create and configure logger
        LOG_Format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename = self.config.getLogConfig('logFile'),
                            level = self.config.getLogConfig('logLevel'),
                            format = LOG_Format)

        self.log = logging.getLogger()

        self.lcd = LcdDriver()
        self.keypad = KeypadDriver()

        self.userVerified = Authenticator().verified()

    def remoteShutdown(self):
        """
        Method to run a remote shutdown of hosts via SSH. Uses CSV file specified in config.ini
        """
        pass
    def remotePowerOn(self):
        """
        Method to run a remote power on of hosts. Uses CSV file specified in config.ini.
        """
        pass
    def mainMenu(self):
        """
        Main Menu for HLPC Program allows user to select operation to run via LCD screen and keypad
        """
        keypad = self.keypad
        lcd = self.lcd
        log = self.log
        userVerified = self.userVerified #Will return true or false depending on if user could be verified

        mainMenuPages = [['Shutdown: A', 'PowerOn: B']] #Text to show depending on current main menu page, the second index determins top [0] or bottom [1] of LCD
        crntMenuPage = 0
        pressedKey = ''
        pageIncrementKey = '#' #Key on keypad to be used to change mainMenuPage

        lcd.print(mainMenuPages[crntMenuPage][0],mainMenuPages[crntMenuPage][1]) #Set initial menu page on LCD
        while(True): #Main loop
            pressedKey = keypad.press() #Get a keypress from user
            log.debug(f'User pressed {pressedKey} on keypad')

            if(pressedKey == pageIncrementKey): #If user presses the increment page button
                crntMenuPage += 1 #Increment current page
                log.debug(f'User incremented main menu page via keypad')
                if(crntMenuPage >= len(mainMenuPages)): #If at last page in menu go to the first page
                    crntMenuPage = 0
                    log.debug(f'Current page is {crntMenuPage}')
            
            else: #Check if user selected an option from menu
                if (pressedKey == 'A'): #If user presses A
                    lcd.print('HLPC Shutdown', 'Loading...')
                    log.info(f'User has selected HLPC Shutdown')
                    time.sleep(2)
                    if(userVerified): #If user can be verified then proceed with shutdown
                        self.remoteShutdown()
                elif (pressedKey == 'B'):
                    lcd.print('HLPC Power On', 'Loading...')
                    log.info(f'User has selected HLPC Power On')
                    time.sleep(2)
                    if(userVerified):
                        self.remotePowerOn()

                else:
                    lcd.clear()
                    lcd.print('Unkown Input','')
                    time.sleep(1)
            
            lcd.clear()
            lcd.print(mainMenuPages[crntMenuPage][0],mainMenuPages[crntMenuPage][1]) #Update main menu

if(__name__ == "__main__"):
    mainHLPC = HLPC()
    mainHLPC.mainMenu()
