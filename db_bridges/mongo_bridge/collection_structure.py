import abc
import logging


class CollectionStructure(abc.ABC):
    def __init__(self):
        self.name = self.set_name()
        self.__unique_fields = self.set_unique_fields()
        self.__data_fields = self.set_data_fields()

    @abc.abstractmethod
    def set_name(self):
        # For Example: return 'collectionA'
        raise NotImplementedError

    @abc.abstractmethod
    def set_unique_fields(self):
        # {'key': 'type'} For Example: return {'a': int(), 'b': str}
        raise NotImplementedError

    @property
    def unique_fields(self):
        return self.__unique_fields

    @abc.abstractmethod
    def set_data_fields(self):
        # {key: default_value} For Example: return {'c': 123}
        raise NotImplementedError

    @property
    def data_fields(self):
        return self.__data_fields

    def document_operator(self, **kwargs):
        document_dict = {}
        document_dict.update(self.__data_fields)
        try:
            for field in self.__unique_fields.keys():
                document_dict[field] = kwargs[field]
        except KeyError as e:
            logging.error(f'The unique field, {e}:{self.__unique_fields[e]}, is not included in kwargs.')
            return None

        for field in self.__data_fields.keys():
            try:
                document_dict[field] = kwargs[field]
            except KeyError as e:
                logging.warning((f'The data field, {e}, is not included in kwargs. '
                                 f'So use the default value for this.'))

        return document_dict


class TryThis(CollectionStructure):
    def set_name(self):
        return 'monthly'

    def set_unique_fields(self):
        return ['a', 'b']

    def set_data_fields(self):
        return ['c', 'd']


if __name__ == '__main__':
    a = TryThis()
    print(a.name)
    print(a.key_fields)

    print(a.data_fields)