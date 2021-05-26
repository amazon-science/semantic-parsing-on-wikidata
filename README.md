## Semantic Parsing on Wikidata
This software package provides utilities to support semantic parsing tasks targeting Wikidata.

### SPARQL to FunQL
According to [Guo, Jiaqi, et al. "Benchmarking Meaning Representations in Neural Semantic Parsing." EMNLP 2020](https://www.aclweb.org/anthology/2020.emnlp-main.118/), "Neural Semantic Parsing approaches exhibit notably different performance when they are trained to generate different meaning representations".
In particular, in the authors conclude that: "according to our experimental results, FunQL tends to outperform Lambda Calculus and Prolog in neural semantic parsing. Additionally, FunQL is relatively robust against program alias. Hence, when developers need to design an MR for a new domain, FunQL is recommended to be the first choice."

This software package allows to compile a SPARQL query into a FunQL query, and back from a FunQL query into a SPARQL query.

As an example, let's take the SPARQL for the question _"What is the population of the capital of France?"_ :

```
SELECT ?ans_0 WHERE {
   wd:Q142 wdt:P36   ?x_0   .
   ?x_0    wdt:P1082 ?ans_0 .
}
```


```python
from semantic_parsing.sparql.sparql_to_mrl import sparql_to_mrl

sparql_to_mrl('SELECT ?ans_0 WHERE { wd:Q142 wdt:P36 ?x_0 . ?x_0 wdt:P1082 ?ans_0 . }')

Out: wd.predicate.*wdt:P1082(wd.predicate.*wdt:P36(wd:Q142))
```

```python
from semantic_parsing.sparql.mrl_to_sparql import mrl_to_sparql

mrl_to_sparql('wd.predicate.*wdt:P1082(wd.predicate.*wdt:P36(wd:Q142))')

Out: SELECT ?ans_0 WHERE { wd:Q142 wdt:P36 ?x_0 . ?x_0 wdt:P1082 ?ans_0 . }
```

### Wikidata Entity Linking
In an open-world semantic parsing task, it is often necessary to link entity mentions to specific entity IDs in Wikidata.
This software package provides the simplest rule-based baseline implementation for this task.

The pre-processing script merges each of the Wikidata entities with their Wikipedia page-views in a given time window (default: one week).

This allows to generate a gazetteer that returns all the possible entities that can be denoted by a given mention, sorted by their number of page-views on Wikipedia, optionally filtered by class or property constraints.

For distinctive names the entity linking is not ambiguous:

```
from semantic_parsing.wikidata.linker import EntityLinker

el = EntityLinker()

el.link_entity('Barack Obama')

Out: ['Q76']
```

Less distinctive names can denote several entities:

```
el.link_entity('Donald Trump')

Out: ['Q22686', 'Q5295230', 'Q23001025', 'Q27947481']
```
In the above case we take advantage of the disambiguation given by the higher popularity of the entity ``Q22686`` (Donald Trump, 45th president of the United States) on Wikipedia.

When the same mention can denote entities of different classes, the popularity alone is not sufficient. For example:

```
el.link_entity('Paris')

Out: ['Q483020', 'Q90', 'Q167646', 'Q923849', 'Q830149', 'Q3305306', 'Q1818121', 'Q1018504', 'Q1341876', 'Q520621', 'Q1931701', 'Q28337101', 'Q3181341', 'Q576584', 'Q1132962', 'Q366081', 'Q1451948', 'Q2300075', 'Q1158980', 'Q934294', 'Q79917', 'Q2052318', 'Q984459', 'Q162121', 'Q7137165', 'Q7137187', 'Q18533474', 'Q22317569', 'Q930765', 'Q960025', 'Q7137190', 'Q7137175', 'Q1124162', 'Q7137184', 'Q7137197', 'Q538772', 'Q7137186', 'Q18331346', 'Q631707', 'Q60751943', 'Q3382754', 'Q10981622', 'Q3365241', 'Q20709367', 'Q7137185', 'Q7137192', 'Q7137172', 'Q151298', 'Q7137164', 'Q15119639', 'Q974043', 'Q7137161', 'Q1628773', 'Q7137189', 'Q30621726', 'Q2220917', 'Q20712325', 'Q7137363', 'Q6065229', 'Q7137194', 'Q7137188', 'Q3365238', 'Q3365236', 'Q2219239']
```

Where:
* ``Q483020``: Paris Saint-Germain F.C., association football club in Paris, France.
* ``Q90``: Paris, capital and largest city of France.

In these cases, we will want to specify semantic constraints either using a class or property that the entity should have.


In certain semantic parsing applications the understanding does provide also an explicit class constraint.
For example, we might know that the mention should be linked to an entity of class ``Q476028`` (association football club):

```
el.link_entity('Paris', class_name='Q476028')

Out: ['Q483020']
```

Alternatively, in other semantic parsing applications, we might just know what properties the entity should have, similarly to using duck typing.

For example, looking up for entities denoted by the mention  _"Paris"_  that have the property ``P1082`` (population), we get:

```
el.link_entity('Paris', , property_name='P1082')

Out: ['Q90', 'Q830149', 'Q3305306', 'Q1018504', 'Q3181341', 'Q576584', 'Q934294', 'Q79917', 'Q984459', 'Q960025', 'Q7137175', 'Q538772', 'Q7137172', 'Q2220917', 'Q2219239']
```

### Setup
Install:
* Install dependencies (rdflib): ``pip install -r requirements.txt``
* [Optional] Specify your preferred data directory (default: ./data): ``export DATA_DIR=/path/to/data/dir``

Pre-process Wikidata:

```
python src/semantic_parsing/wikidata/preprocess.py
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

