# Add a new implementation engine to the ontology

## Information needed


* Parameters and format specific to the implementation engine

## Steps

1. Create a new folder named as the new engine on [`ontology_populator/implementations`](../ontology_populator/implementations/)
2. In this new folder, create `<engine name>_implementation.py`.
3. Create new classes tha inherit from the concepts defined [here](../ontology_populator/implementations/core/) that fullfil the needs of the new engine. Use [`knime_implementation.py`](../ontology_populator/implementations/knime/knime_implementation.py) as a reference. The new classes should contain all the information needed for the translation step.
4. In `ontology_populator/implementations/<engine name>/`, create the script `__init__.py` and leave it empty.
5. [Add new algorithms](createNewAlgorithm.md) specific to the engine.