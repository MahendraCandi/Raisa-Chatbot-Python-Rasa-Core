import json
import os
import pymongo
from typing import Optional, Text, Dict, List, Union

import rasa.data
from rasa.core.domain import Domain
from rasa.core.interpreter import RegexInterpreter, NaturalLanguageInterpreter
from rasa.core.training.structures import StoryGraph
from rasa.core.training.dsl import StoryFileReader
from rasa.importers.importer import TrainingDataImporter
from rasa.nlu.training_data import TrainingData
import tempfile
import rasa.utils.io as io_utils


class MongoImporter(TrainingDataImporter):
    def __init__(self,
                 config_path: Optional[Text]=None,
                 domain_path: Optional[Text]=None,
                 training_data_path: Optional[Union[List[Text], Text]]=None):

        directory = tempfile.mkdtemp()
        self.extract_nlu(directory)
        self.extract_story(directory)
        self.story_files, self.nlu_files = rasa.data.get_core_nlu_files([directory])

    # def get_files_from(self, directory: Text) -> List[ContentFile]:
    #     files = []
    #     for f in self.repository.get_contents(directory):
    #         if f.type == "file":
    #             files.append(f)
    #         else:
    #             files += self.get_files_from(f.path)
    #     return files

    @staticmethod
    def extract_nlu(directory):
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
        # print(f'CLIENT: {client}')
        # print(f'CLIENT: {client.list_database_names()}')
        mydb = client["rasaMongo"]
        # print(f'MYDB: {mydb}')
        # print(f'MYDB: {mydb.list_collection_names()}')
        # print(f'MYDB: {mydb.list_collections()}')
        # cursor = mydb["training_data"].find({})
        training_data = {}
        for x in mydb["training_data"].find({}):
            if x.get('nlu_data') is not None:
                training_data = x.get('nlu_data')
        # print(f'TRAINING DATA: {training_data}')
        # print(f'DIRECTORY: {directory}')
        with open(os.path.join(directory, 'nlu_training_data.json'), 'w') as file:
            # print(f'FILE: {file.name}')
            json.dump(training_data, file)

    @staticmethod
    def extract_story(directory):
        files = {}
        path_stories = "data/stories"
        for filename in os.listdir(path_stories):
            # print(f'FILE NAME: {filename}')
            # and filename.endswith(".md"):
            # if os.path.isfile(filename):
            if filename.endswith(".md"):
                # print(f'FILE NAME: {filename}')
                with open(os.path.join(path_stories, filename), 'r') as file:
                    # print(file.read())
                    files[filename] = file.read()
        # print(f'FILES: {files}')

        for filename, value in files.items():
            with open(os.path.join(directory, filename), 'w') as file:
                file.write(value)

    async def get_stories(self, interpreter: "NaturalLanguageInterpreter" = RegexInterpreter(),
                          template_variables: Optional[Dict] = None, use_e2e: bool = False,
                          exclusion_percentage: Optional[int] = None) -> StoryGraph:
        story_steps = await StoryFileReader.read_from_files(
            self.story_files,
            await self.get_domain(),
            interpreter,
            template_variables,
            use_e2e,
            exclusion_percentage
        )
        return StoryGraph(story_steps)

    async def get_nlu_data(self, language: Optional[Text] = "en") -> TrainingData:
        # return rasa_utils.training_data_from_paths(self.nlu_files, language)
        from rasa.importers import utils

        return utils.training_data_from_paths(self.nlu_files, language)

    async def get_domain(self) -> Domain:
        # domain_as_yaml = self.get_content("domain.yml")
        # return Domain.from_yaml(domain_as_yaml)
        return Domain.from_file("domain.yml")
        # pass

    # def get_content(self, path: Text) -> Text:
    #     file = self.repository.get_contents(path)
    #     return file.decoded_content.decode("utf-8")

    async def get_config(self) -> Dict:
        config_as_yaml = io_utils.read_yaml_file("config.yml")
        return config_as_yaml
        # pass
