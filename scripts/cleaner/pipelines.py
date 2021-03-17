class BasePipeline:
    def __call__(self, word_frequency):
        return word_frequency


class EnglishPipeline(BasePipeline):
    pass


class SpanishPipeline(BasePipeline):
    pass


class GermanPipeline(BasePipeline):
    pass


class FrenchPipeline(BasePipeline):
    pass


class PortuguesePipeline(BasePipeline):
    pass


class RussianPipeline(BasePipeline):
    pass
