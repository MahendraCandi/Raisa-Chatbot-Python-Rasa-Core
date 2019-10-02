import logging
import os
from typing import Optional, Text, Dict, List, Union

from github import Github
from github.ContentFile import ContentFile

import rasa.data
from rasa.core.domain import Domain
from rasa.core.interpreter import RegexInterpreter, NaturalLanguageInterpreter
from rasa.core.training.structures import StoryGraph
from rasa.core.training.dsl import StoryFileReader
from rasa.importers.importer import TrainingDataImporter
from rasa.nlu.training_data import TrainingData
import tempfile
import rasa.utils.io as io_utils

# import os
# import tempfile
# import rasa.data oke
# import rasa.utils.io as io_utils
# from typing import Optional, Text, Dict, List, Union
#
# from github import Github
# from github.ContentFile import ContentFile
# from rasa.core.domain import Domain oke
# from rasa.core.interpreter import RegexInterpreter
# from rasa.core.training import StoryGraph
# from rasa.core.training.dsl import StoryFileReader
# from rasa.importers.importer import TrainingDataImporter
# from rasa.nlu.training_data import TrainingData


class GitImporter(TrainingDataImporter):
    def __init__(self,
                 config_path: Optional[Text]=None,
                 domain_path: Optional[Text]=None,
                 training_data_path: Optional[Union[List[Text], Text]]=None,
                 repository=""):
        github = Github()
        self.repository = github.get_repo(repository)

        data_files = self.get_files_from("data")
        logging.debug(f'DATA FILES: {data_files}')
        directory = tempfile.mkdtemp()
        for f in data_files:
            with open(os.path.join(directory, f.name), "w+b") as file:
                file.write(f.decoded_content)
        logging.debug(f'DIRECTORY: {directory}')
        self.story_files, self.nlu_files = rasa.data.get_core_nlu_files([directory])

    def get_files_from(self, directory: Text) -> List[ContentFile]:
        files = []
        for f in self.repository.get_contents(directory):
            if f.type == "file":
                files.append(f)
            else:
                files += self.get_files_from(f.path)
        return files

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

    def get_content(self, path: Text) -> Text:
        file = self.repository.get_contents(path)
        return file.decoded_content.decode("utf-8")

    async def get_config(self) -> Dict:
        config_as_yaml = io_utils.read_yaml_file("config.yml")
        return config_as_yaml
        # pass
