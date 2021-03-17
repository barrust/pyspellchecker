import os
import traceback

from .pipelines import (BasePipeline, EnglishPipeline, FrenchPipeline,
                        GermanPipeline, PortuguesePipeline, RussianPipeline,
                        SpanishPipeline)


class Cleaner:
    script_path = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.abspath("{}/../../".format(script_path))
    resources_path = os.path.abspath("{}/resources/".format(module_path))
    data_path = os.path.abspath("{}/data/".format(script_path))

    def __init__(self, language) -> None:
        self.language = language
        self.exclude_filepath = os.path.abspath("{}/{}_exclude.txt".format(self.data_path, language))
        self.include_filepath = os.path.abspath("{}/{}_include.txt".format(self.data_path, language))
        self.misfit_filepath = os.path.abspath("{}/{}_misfit.txt".format(self.data_path, language))

        self.pipeline = self._get_pipeline(language)

    def _get_pipeline(self, language) -> BasePipeline:
        pipelines = {
            'en': EnglishPipeline,
            'fr': FrenchPipeline,
            'de': GermanPipeline,
            'pt': PortuguesePipeline,
            'ru': RussianPipeline,
            'es': SpanishPipeline,
        }
        try:
            lang_pipeline = pipelines[language]
        except KeyError as e:
            langs = ' '.join(pipelines.keys())
            traceback.print_exc()
            raise Exception("{} language is not supported.\n"
                            "Please, use one this".format(language, langs))
        # TODO: init pipeline
        return lang_pipeline()

    def clean(self, word_frequency):
        return self.pipeline(word_frequency)
