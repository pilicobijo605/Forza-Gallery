import re
import unicodedata

_PROFANITY = {
    "puta","puto","putos","putas","hdp","hijodeputa",
    "mierda","mierdas","gilipollas","gilipolla","coño","joder","hostia",
    "imbecil","imbeciles","idiota","idiotas","estupido","estupida",
    "culo","culos","polla","pollas","tonto","tontos","tonta","tontas",
    "zorra","zorras","cabron","cabrona","cabrones","pendejo","pendejos",
    "maricon","maricones","subnormal","retrasado","retrasada","mongolo",
    "capullo","capullos","mamon","mamones","inutil","inutiles",
    "pederasta","prostituta","whore","bastardo","bastarda",
}

def _norm(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))

_NORMALIZED = {_norm(w) for w in _PROFANITY}

def contains_profanity(text: str) -> bool:
    normalized = _norm(text)
    words = re.findall(r'\b\w+\b', normalized)
    return any(w in _NORMALIZED for w in words)
