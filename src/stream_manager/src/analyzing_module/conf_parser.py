import configparser
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.ERROR)

class ConfParser() :

    def __init__(self,  config_path):
        self._config_path = config_path
        self._config = configparser.ConfigParser()
        self._parameters = {}

    def _readConfig(self) :
        try:
            self._config.read(self._config_path)
        except Exception as e :
            print(str(e))
        
        self._parameters['opencv'] = self._config.get('model', 'opencv')
        self._parameters['identification'] = self._config.get('model', 'identification')
        self._parameters['scaleFactor'] = self._config.get('model', 'scaleFactor')
        self._parameters['minNeighbours'] = self._config.get('model', 'minNeighbours')

        if self._check_parameters() == False :
            raise ("Invalid parameters")
            
        return self._parameters

    def _check_parameters(self):
        if self._parameters['opencv'] != True and self._parameters['opencv'] != False :
            return False
        if self._parameters['identification'] != True and self._parameters['identification'] != False:
            return False
        try :
           self._parameters['scaleFactor'] = float(self._parameters['scaleFactor'] )
        except ValueError :
            return False
        
        try : 
            self._parameters['minNeighbours'] = int( self._parameters['minNeighbours'])
        except:
            return False
        
        return True