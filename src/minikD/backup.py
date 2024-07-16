import os
from datetime import datetime, time, timedelta
import checksumdir
import subprocess
from logger import my_logger


LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../logs/minik.log')

class Backup:
    def __init__(self, logger, backup_time = 5):
        self.last_backup_time = datetime.now() - timedelta(days=1)
        self.backup_time = backup_time
        self.logger = logger

    def __extract_datetime_from_directory_name(self, directory_name, world_name):
        try:
            return datetime.strptime(directory_name, f"{world_name}_%d.%m.%Y-%H_%M_%S")
        except ValueError:
            return None	

    def __get_all_directories_sorted(self, backup_path, world_name):
        directories = [d for d in os.listdir(backup_path) if os.path.isdir(os.path.join(backup_path, d))]
        dated_directories = [(d, self.__extract_datetime_from_directory_name(d, world_name)) for d in directories]
        dated_directories = [(d, dt) for d, dt in dated_directories if dt is not None]
        dated_directories.sort(key=lambda x: x[1])
        return dated_directories 

    def __is_world_changed(self, path_1, path_2):
        return checksumdir.dirhash(path_1) != checksumdir.dirhash(path_2) 

    def __remove_excess_backups(self, backup_path, world_name, backups_count):
        backups = self.__get_all_directories_sorted(backup_path, world_name)
        while len(backups) > backups_count:
            self.logger.debug(f"[BACKUP] File {backups[0][0]} deleted")
            subprocess.run(['rm', '-r', os.path.join(backup_path, backups[0][0])])
            backups = self.__get_all_directories_sorted(backup_path, world_name)

    def __copy_world(self, world_path, backup_path, world_name):
        self.logger.debug(f"[BACKUP] Copying {world_path} to {backup_path}")
        subprocess.run(['cp', '-r', world_path, backup_path])
        subprocess.run(['mv', os.path.join(backup_path, world_name),  os.path.join(backup_path, datetime.now().strftime(f"{world_name}_%d.%m.%Y-%H_%M_%S"))])

    def backup(self, server_path, backup_path, world_name, backups_count):
        world_path = os.path.join(server_path, world_name)
        backups = self.__get_all_directories_sorted(backup_path, world_name)
        
        if not backups:
            self.__copy_world(world_path, backup_path, world_name)
            return
        last_backup = backups[len(backups)-1]
        backup_world_path = os.path.join(backup_path, last_backup[0])

        if self.__is_world_changed(world_path, backup_world_path):
            self.__copy_world(world_path, backup_path, world_name)
            self.__remove_excess_backups(backup_path, world_name, backups_count)
        else:
            new_name = datetime.now().strftime(f"{world_name}_%d.%m.%Y-%H_%M_%S")
            self.logger.debug(f"[BACKUP] Renaming {world_name} to {new_name}")
            subprocess.run(['mv', backup_world_path,  os.path.join(backup_path, new_name)]) # rename last backup
        
    def is_ready(self):
        if(self.last_backup_time.date() != datetime.now().date()) and \
                (datetime.now().time() > time(self.backup_time)) and \
                datetime.now().time() < (datetime.combine(datetime.today(), time(self.backup_time)) + timedelta(hours=1)).time():
            self.last_backup_time = datetime.now()
            return True
        return False

