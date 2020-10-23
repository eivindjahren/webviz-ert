from ertviz.data_loader import get_data, get_schema, get_csv_data
from ertviz.models import Response

from ertviz.models.parameter_model import (
    PriorModel,
    ParameterRealizationModel,
    ParametersModel,
)


def get_parameter_models(parameters_schema):
    parameters = {}
    for param in parameters_schema:
        group = param["group"]
        key = param["key"]
        prior = None
        if param["prior"]:
            prior = PriorModel(
                param["prior"]["function"],
                param["prior"]["parameter_names"],
                param["prior"]["parameter_values"],
            )
        parameters[key] = ParametersModel(
            group=group, key=key, prior=prior, schema_url=param["ref_url"]
        )
    return parameters


class EnsembleModel:
    def __init__(self, ref_url):
        schema = get_schema(api_url=ref_url)
        self._name = schema["name"]
        self._id = ref_url  # ref_url
        self._children = schema["children"]
        self._parent = schema["parent"]
        self.responses = {
            resp_schema["name"]: Response(
                name=resp_schema["name"], ref_url=resp_schema["ref_url"]
            )
            for resp_schema in schema["responses"]
        }
        self.parameters = get_parameter_models(schema["parameters"])

    @property
    def children(self):
        if hasattr(self, "_cached_children"):
            return self._cached_children
        self._cached_children = [
            EnsembleModel(ref_url=child["ref_url"]) for child in self._children
        ]
        return self._cached_children

    @property
    def parent(self):
        if hasattr(self, "_cached_parent"):
            return self._cached_parent
        self._cached_parent = EnsembleModel(ref_url=self.parent["ref_url"])
