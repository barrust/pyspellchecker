import os
import traceback

from pipelines import (BasePipeline, EnglishPipeline, FrenchPipeline,
                       GermanPipeline, PortuguesePipeline, RussianPipeline,
                       SpanishPipeline)


class Cleaner:
    script_path = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.abspath("{}/../".format(script_path))
    resources_path = os.path.abspath("{}/resources/".format(module_path))
    data_path = os.path.abspath("{}/data/".format(module_path))

    def __init__(self, language) -> None:
        self.language = language

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
        exclude_path = os.path.abspath("{}/{}_exclude.txt".format(self.data_path, language))
        include_path = os.path.abspath("{}/{}_include.txt".format(self.data_path, language))
        misfit_path = os.path.abspath("{}/{}_misfit.txt".format(self.data_path, language))
        return lang_pipeline(exclude_path, include_path, misfit_path)

    def clean(self, word_frequency):
        return self.pipeline(word_frequency)


if __name__ == '__main__':
    wf = {
        "α3β4-рецептора": 1,
        "β": 1,
        "β-hgs": 1,
        "β-klotho": 4,
        "β-адренэргический": 1,
        "β-адренэргического": 1,
        "β-амилоиды": 1,
        "β-гидроксибутират": 3,
        "β-гидроксибутирата": 2,
        "β-гидроксибутиратом": 1,
        "β-гидроксилаза": 2,
        "β-гидроксилазы": 2,
        "β-каротин": 1,
        "β-каротина": 1,
        "β-катенин": 1,
        "β-кетокислоты": 1,
        "β-криптоксантин": 1,
        "β2pkc": 1,
        "ε": 1,
        "κυπε": 1,
        "λ": 1,
        "λb": 2,
        "λcdm": 6,
        "λcdm-модель": 1,
        "μ": 1,
        "μ-опиоидные": 1,
        "μετεμψύχωσις": 1,
        "π": 1,
        "προς": 2,
        "ρικ": 1,
        "ρώσους": 2,
        "σ_σ": 1,
        "σb": 3,
        "ψ-мезон": 2,
        "а": 30849,
        "а-100лл": 8,
        "а-10c": 1,
        "а-10а": 4,
        "а-10с": 7,
        "а-18e": 1,
        "а-190э": 8,
        "а-192м": 14,
        "а-1м": 3,
        "а-20g": 1,
        "а-220м": 4,
        "а-319-115xcj": 3,
        "а-350р": 1,
        "а-35м": 2,
        "а-400м": 3,
        "а-50и": 1,
        "а-50м": 3,
        "а-50у": 47,
        "а-50э": 1,
        "а-50эи": 21,
        "а-74т-200а": 1,
        "а-7а": 2,
        "а-day": 1,
        "а-ha": 1,
        "а-mobile": 2,
        "а-si": 1,
        "а-а-а": 3,
        "а-а-а-а-ах": 1,
        "а-а-а-апчихуа": 1,
        "а-аа": 5,
        "а-ав": 5,
        "а-асара": 2,
        "а-б": 5,
        "а-брендами": 1,
        "а-вым": 1,
        "а-гай": 1,
        "а-групп": 5,
        "а-дин": 11,
        "а-дура": 2,
        "а-дуры": 1,
    }
    cleaner = Cleaner('ru')
    mf = cleaner.clean(wf)
    # dump wf
    # dump mf
