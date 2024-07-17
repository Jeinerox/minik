import yaml
import os
import logging
import re



class YamlTester:
    def __init__(self, file_path, logger):
        self.file_path = file_path
        self.logger = logger
        
        self.required_fields = ['name', 'path', 'memory', 'auto_restart', 'start_on_launch']
        self.default_data = \
        'servers:\n- name: default \n  path: \\your\\mc\\folder\\path\n  memory: -Xmx1G\n  auto_restart: false\n  start_on_launch: false'
        self.previous_config = None
        self.is_previous_good = True

    def __check_folder(self):
        if not os.path.isfile(self.file_path):
            self.logger.warn(f"[YAML] Config not exist. Creating a new one.")
            os.makedirs(os.path.dirname(self.file_path))
            with open(self.file_path, 'w') as file:
                file.write(self.default_data)

    def __check_yaml_fields(self):
        with open(self.file_path, 'r') as file:        
            try:
                file.seek(0)
                data = yaml.safe_load(file)
            except yaml.YAMLError as e:
                self.logger.error(f"[YAML] Error reading the YAML file: {e}")
                return None
            
            if data == self.previous_config:
                if self.is_previous_good:
                    return data
                return None
            else:
                self.previous_config = data


            '''    FIELDS CHECKING    '''

            if 'servers' not in data:
                self.logger.error("[YAML] There is no \"servers\" array in config")
                return None    

            error = False
            for server in data['servers']:
                if 'name' not in server or server['name'] == None:
                    self.logger.error(f"[YAML] There is no \"name\" field in config or it's empty.")
                    error = True
                    continue
                for field in self.required_fields:
                    if field not in server:
                        self.logger.error(f"[YAML] There is no \"{field}\" field in {server['name']}'s config.")
                        error = True

                if error:
                    continue

                '''    INFO CHECKING    '''
        
                ''' path '''
                server_jar_path = os.path.join(server['path'], 'server.jar')
                if not os.path.isfile(server_jar_path):
                    self.logger.error(f"[YAML] There is an error in the path field in {server['name']}'s config: The file \"server.jar\" was not found in {server['path']}.")
                    error = True

                ''' memory '''
                pattern = r"^-Xmx\d+(?:[kKmMgG])?$"
                if not bool(re.match(pattern, server['memory'])):
                    self.logger.error(f"[YAML] There is an error in the memory field in {server['name']}'s config: {server['memory']}. Example: -Xmx2G")
                    error = True

                ''' bin's '''
                if type(server['auto_restart']) != bool:
                    self.logger.error(f"[YAML] There is an error in the auto_restart field in {server['name']}'s config. Value should be boolean \"true\" or \"false\", not \"{server['auto_restart']}\".")
                    error = True
                if type(server['start_on_launch']) != bool:
                    self.logger.error(f"[YAML] There is an error in the start_on_launch field in {server['name']}'s config. Value should be boolean \"true\" or \"false\", not \"{server['start_on_launch']}\".")
                    error = True

                '''   optional checks   '''
                
                ''' backup_limit '''
                if 'backup_limit' in server and type(server['backup_limit']) != int:
                    self.logger.error(f"[YAML] There is an error in the backup_limit field in {server['name']}'s config. Value should be integer like \"1\" or \"34\", not \"{server['backup_limit']}\".")
                    error = True    

                ''' backup_path '''           
                if 'backup_path' in server and not os.path.exists(server['backup_path']):
                    self.logger.error(f"[YAML] There is an error in the backup_path field in {server['name']}'s config. No such directory: {server['backup_path']}.")
                    error = True

                ''' world_name '''           
                if 'world_name' in server and not os.path.exists(os.path.join(server['path'], server['world_name'])):
                    self.logger.error(f"[YAML] There is an error in the world_name field in {server['name']}'s config. No such directory: {os.path.join(server['path'], server['world_name'])}.")
                    error = True    

            if error:
                self.is_previous_good =False
                return None
            self.logger.debug(f"[YAML] Config successfully loaded.")            
            self.is_previous_good = True
            return data



    def safe_read_yaml(self):
        self.__check_folder()
        return self.__check_yaml_fields()

if __name__ == "__main__":
    CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../config/servers.yaml')

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG) 
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    tester = YamlTester(CONFIG_PATH, logger)
    import time
    start_time = time.time()  
    print(tester.safe_read_yaml())
    print(f"Test execution time: {time.time() - start_time}")

