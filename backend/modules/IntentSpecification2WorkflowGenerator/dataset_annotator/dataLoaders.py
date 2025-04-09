from abc import abstractmethod
import csv
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import zipfile
import tempfile
import shutil
import atexit


# Create a temporary directory
temp_dir = tempfile.mkdtemp()

# Register a cleanup function that will delete the directory upon exit
def cleanup_temp_dir():
    if Path(temp_dir).is_dir():
        shutil.rmtree(temp_dir)
        print(f"Temporary directory {temp_dir} cleaned up.")

atexit.register(cleanup_temp_dir)

print(f"Temporary directory created: {temp_dir}")


class DataLoader:
    fileFormat = "data file"

    def __init__(self,file):
        self.file_path = Path(file).resolve().as_posix()
        self.metadata = {
            "fileFormat": self.fileFormat,
            "path": self.file_path
        }

    @abstractmethod
    def getDataFrame(self) -> pd.DataFrame:
        pass

    def getFileMetadata(self) -> Dict:
        return self.metadata
    
    
class CSVLoader(DataLoader):
    fileFormat = "CSV"

    def __init__(self,file):
        super().__init__(file)

        with open(self.file_path, 'r') as csvfile:
            self.encoding = csvfile.encoding
            lines = [csvfile.readline() for _ in range(50)]
        
        self.dialect = csv.Sniffer().sniff(''.join(lines))
        self.hasHeader = csv.Sniffer().has_header(''.join(lines))


    def getDataFrame(self) -> pd.DataFrame:
        return pd.read_csv(self.file_path, encoding=self.encoding, delimiter=self.dialect.delimiter)
    
    def getFileMetadata(self):
        metadata = {
            **self.metadata,
            "delimiter": self.dialect.delimiter,
            "doubleQuote": self.dialect.doublequote,
            "lineDelimiter": self.dialect.lineterminator,
            "quoteChar": self.dialect.quotechar,
            "skipInitialSpace": self.dialect.skipinitialspace,
            "encoding": self.encoding,
            "hasHeader": self.hasHeader,
        }

        return metadata
    
class ParquetLoader(DataLoader):
    fileFormat = "Parquet"

    def getDataFrame(self):
        return pd.read_parquet(self.file_path)
    

class FolderLoader(DataLoader):
    fileFormat = "Folder"

    def __init__(self,dir):
        super().__init__(dir)
        self.data_loaders: list[DataLoader] = [get_loader(file.as_posix()) for file in Path(dir).iterdir()]

    def getDataFrame(self):
        dfs: list[pd.DataFrame] = []
        for dl in self.data_loaders:
            dfs.append(dl.getDataFrame())
        
        return pd.concat(dfs)
    
    def getFileMetadata(self):

        child_metadata = {}
        for i,dl in enumerate(self.data_loaders):
            dl_metadata = dl.getFileMetadata()
            for key, value in dl_metadata.items():
                child_metadata[f'file_{i}_{key}'] = value
        
        metadata = {
            ** self.metadata,
            "numFiles": len(self.data_loaders),
            ** child_metadata,
        }

        return metadata
    
class ZipLoader(FolderLoader):
    fileFormat = "ZIP"

    def __init__(self,dir):
        zfile = zipfile.ZipFile(dir, mode='r')
        extraction_path = Path(temp_dir).joinpath(Path(dir).with_suffix('').name)
        zfile.extractall(extraction_path)
        super().__init__(extraction_path)
        self.metadata['path'] = Path(dir).resolve().as_posix()


class DummyLoader(DataLoader):
    fileFormat = "Unsupported"
    
    def getDataFrame(self):
        return pd.DataFrame()
    
    def getFileMetadata(self):
        metadata = {
            **self.metadata,
            "ignored": True
        }
        return metadata

            



###################################################################
    
loaders = {
    "csv": CSVLoader,
    "parquet": ParquetLoader,
    "zip": ZipLoader,
    "": FolderLoader,
}


def get_extension(file_path) -> str:
    extension = Path(file_path).suffix
    return extension[1:]

def get_loader(path:Path) -> DataLoader:

    if Path(path).is_dir():
        return FolderLoader(path)
    
    extension = get_extension(path)
    print(loaders.get(extension,DummyLoader))
    return loaders.get(extension,DummyLoader)(path)