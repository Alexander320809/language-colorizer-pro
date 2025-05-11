# app_streamlit.py
import streamlit as st
import re
import json
import os
from functools import lru_cache
import pdfplumber

from youtube_transcript_api import YouTubeTranscriptApi
import requests
import tempfile

# ====================== CONFIGURACIÓN INICIAL ======================
# 2. Configuración de página INMEDIATAMENTE después de los imports
st.set_page_config(
    page_title="Language Colorizer Pro",
    layout="wide",
    page_icon="🎨"
)

PALABRAS_COLORES_JSON = "palabras_colores.json"

# ====================== CATEGORÍAS GRAMATICALES ======================
CATEGORIAS = {
    "verbos": "#00AA00",         # Verde
    "sustantivos": "purple",     # Morado
    "pronombres": "red",         # Rojo
    "articulos": "blue",         # Azul
    "conjunciones": "#8B4513",   # Marrón
    "adjetivos": "#FFC0CB",      # Rosado
    "adverbios": "#FFA500",      # Naranja
    "preposiciones": "#FFFF00"   # Amarillo
}

# ====================== DICCIONARIO BASE DE PALABRAS ======================
palabras_base = {
    # Verbos (verde)

    "be": "#00AA00", "am": "#00AA00", "do": "#00AA00", "have": "#00AA00", "go": "#00AA00",
    "will": "#00AA00", "can": "#00AA00", "get": "#00AA00", "like": "#00AA00", "know": "#00AA00",
    "want": "#00AA00", "think": "#00AA00", "say": "#00AA00", "see": "#00AA00", "make": "#00AA00",
    "come": "#00AA00", "look": "#00AA00", "let": "#00AA00", "take": "#00AA00", "would": "#00AA00",
    "use": "#00AA00", "need": "#00AA00", "tell": "#00AA00", "work": "#00AA00", "give": "#00AA00",
    "could": "#00AA00", "should": "#00AA00", "find": "#00AA00", "mean": "#00AA00", "love": "#00AA00",
    "try": "#00AA00", "feel": "#00AA00", "call": "#00AA00", "talk": "#00AA00", "help": "#00AA00",
    "start": "#00AA00", "leave": "#00AA00", "put": "#00AA00", "please": "#00AA00", "show": "#00AA00",
    "happen": "#00AA00", "keep": "#00AA00", "play": "#00AA00", "thank": "#00AA00", "ask": "#00AA00",
    "wait": "#00AA00", "change": "#00AA00", "stop": "#00AA00", "may": "#00AA00", "hear": "#00AA00",
    "move": "#00AA00", "eat": "#00AA00", "live": "#00AA00", "must": "#00AA00", "turn": "#00AA00",
    "run": "#00AA00", "bring": "#00AA00", "might": "#00AA00", "watch": "#00AA00", "open": "#00AA00",
    "laugh": "#00AA00", "stay": "#00AA00", "become": "#00AA00", "believe": "#00AA00", "set": "#00AA00",
    "understand": "#00AA00", "buy": "#00AA00", "meet": "#00AA00", "hold": "#00AA00", "care": "#00AA00",
    "kill": "#00AA00", "remember": "#00AA00", "hope": "#00AA00", "add": "#00AA00", "lose": "#00AA00",
    "learn": "#00AA00", "write": "#00AA00", "check": "#00AA00", "seem": "#00AA00", "create": "#00AA00",
    "read": "#00AA00", "cause": "#00AA00", "follow": "#00AA00", "speak": "#00AA00", "pay": "#00AA00",
    "close": "#00AA00", "send": "#00AA00", "break": "#00AA00", "die": "#00AA00", "win": "#00AA00",
    "hit": "#00AA00", "include": "#00AA00", "forget": "#00AA00", "sit": "#00AA00", "walk": "#00AA00",
    "listen": "#00AA00", "fall": "#00AA00", "click": "#00AA00", "save": "#00AA00", "continue": "#00AA00",
    "share": "#00AA00", "fight": "#00AA00", "cut": "#00AA00", "drink": "#00AA00", "post": "#00AA00",
    "guess": "#00AA00", "build": "#00AA00", "stand": "#00AA00", "grow": "#00AA00", "provide": "#00AA00",
    "support": "#00AA00", "allow": "#00AA00", "wear": "#00AA00", "worry": "#00AA00", "pick": "#00AA00",
    "choose": "#00AA00", "deal": "#00AA00", "sleep": "#00AA00", "drive": "#00AA00", "control": "#00AA00",
    "enjoy": "#00AA00", "finish": "#00AA00", "offer": "#00AA00", "miss": "#00AA00", "lead": "#00AA00",
    "decide": "#00AA00", "pass": "#00AA00", "sell": "#00AA00", "begin": "#00AA00", "spend": "#00AA00",
    "catch": "#00AA00", "return": "#00AA00", "sort": "#00AA00", "lie": "#00AA00", "design": "#00AA00",
    "wish": "#00AA00", "cover": "#00AA00", "pull": "#00AA00", "hurt": "#00AA00", "study": "#00AA00",
    "expect": "#00AA00", "receive": "#00AA00", "suppose": "#00AA00", "sigh": "#00AA00", "visit": "#00AA00",
    "chuckle": "#00AA00", "throw": "#00AA00", "drop": "#00AA00", "consider": "#00AA00", "touch": "#00AA00",
    "wonder": "#00AA00", "attack": "#00AA00", "act": "#00AA00", "trust": "#00AA00", "bear": "#00AA00",
    "reach": "#00AA00", "agree": "#00AA00", "realize": "#00AA00", "cry": "#00AA00", "notice": "#00AA00",
    "focus": "#00AA00", "shoot": "#00AA00", "explain": "#00AA00", "marry": "#00AA00", "join": "#00AA00",
    "ring": "#00AA00", "teach": "#00AA00", "taste": "#00AA00", "push": "#00AA00", "apply": "#00AA00",
    "draw": "#00AA00", "increase": "#00AA00", "hate": "#00AA00", "grunt": "#00AA00", "search": "#00AA00",
    "hang": "#00AA00", "protect": "#00AA00", "release": "#00AA00", "prepare": "#00AA00", "charge": "#00AA00",
    "fly": "#00AA00", "cheer": "#00AA00", "require": "#00AA00", "enter": "#00AA00", "dance": "#00AA00",
    "hide": "#00AA00", "shall": "#00AA00", "remove": "#00AA00", "carry": "#00AA00", "mention": "#00AA00",
    "appear": "#00AA00", "beat": "#00AA00", "fill": "#00AA00", "scream": "#00AA00", "press": "#00AA00",
    "travel": "#00AA00", "connect": "#00AA00", "accept": "#00AA00", "fit": "#00AA00", "fix": "#00AA00",
    "serve": "#00AA00", "cook": "#00AA00", "wake": "#00AA00", "raise": "#00AA00", "jump": "#00AA00",
    "shut": "#00AA00", "ride": "#00AA00", "imagine": "#00AA00", "treat": "#00AA00", "select": "#00AA00",
    "recommend": "#00AA00", "subscribe": "#00AA00", "gasp": "#00AA00", "arrive": "#00AA00", "roll": "#00AA00",
    "smell": "#00AA00", "surprise": "#00AA00", "handle": "#00AA00", "manage": "#00AA00", "develop": "#00AA00",
    "remain": "#00AA00",

    # Verbos en pasado (verde #00AA00)
    "was": "#00AA00", "were": "#00AA00", "did": "#00AA00", "had": "#00AA00", "went": "#00AA00",
    "got": "#00AA00", "liked": "#00AA00", "knew": "#00AA00", "wanted": "#00AA00", "thought": "#00AA00",
    "said": "#00AA00", "saw": "#00AA00", "made": "#00AA00", "came": "#00AA00", "looked": "#00AA00",
    "took": "#00AA00", "used": "#00AA00", "needed": "#00AA00", "told": "#00AA00", "worked": "#00AA00",
    "gave": "#00AA00", "found": "#00AA00", "meant": "#00AA00", "loved": "#00AA00", "tried": "#00AA00",
    "felt": "#00AA00", "called": "#00AA00", "talked": "#00AA00", "helped": "#00AA00", "started": "#00AA00",
    "left": "#00AA00", "showed": "#00AA00", "happened": "#00AA00", "kept": "#00AA00", "played": "#00AA00",
    "thanked": "#00AA00", "asked": "#00AA00", "waited": "#00AA00", "changed": "#00AA00", "stopped": "#00AA00",
    "heard": "#00AA00", "moved": "#00AA00", "ate": "#00AA00", "lived": "#00AA00", "turned": "#00AA00",
    "ran": "#00AA00", "brought": "#00AA00", "watched": "#00AA00", "opened": "#00AA00", "laughed": "#00AA00",
    "stayed": "#00AA00", "became": "#00AA00", "believed": "#00AA00", "understood": "#00AA00", "bought": "#00AA00",
    "met": "#00AA00", "held": "#00AA00", "cared": "#00AA00", "killed": "#00AA00", "remembered": "#00AA00",
    "hoped": "#00AA00", "added": "#00AA00", "lost": "#00AA00", "learned": "#00AA00", "wrote": "#00AA00",
    "checked": "#00AA00", "seemed": "#00AA00", "created": "#00AA00", "read": "#00AA00", "caused": "#00AA00",
    "followed": "#00AA00", "spoke": "#00AA00", "paid": "#00AA00", "closed": "#00AA00", "sent": "#00AA00",
    "broke": "#00AA00", "died": "#00AA00", "won": "#00AA00", "included": "#00AA00", "forgot": "#00AA00",
    "sat": "#00AA00", "walked": "#00AA00", "listened": "#00AA00", "fell": "#00AA00", "clicked": "#00AA00",
    "saved": "#00AA00", "continued": "#00AA00", "shared": "#00AA00", "fought": "#00AA00", "drank": "#00AA00",
    "posted": "#00AA00", "guessed": "#00AA00", "built": "#00AA00", "stood": "#00AA00", "grew": "#00AA00",
    "provided": "#00AA00", "supported": "#00AA00", "allowed": "#00AA00", "wore": "#00AA00", "worried": "#00AA00",
    "picked": "#00AA00", "chose": "#00AA00", "dealt": "#00AA00", "slept": "#00AA00", "drove": "#00AA00",
    "controlled": "#00AA00", "enjoyed": "#00AA00", "finished": "#00AA00", "offered": "#00AA00", "missed": "#00AA00",
    "led": "#00AA00", "decided": "#00AA00", "passed": "#00AA00", "sold": "#00AA00", "began": "#00AA00",
    "spent": "#00AA00", "caught": "#00AA00", "returned": "#00AA00", "sorted": "#00AA00", "lay": "#00AA00",
    "designed": "#00AA00", "wished": "#00AA00", "covered": "#00AA00", "pulled": "#00AA00", "studied": "#00AA00",
    "expected": "#00AA00", "received": "#00AA00", "supposed": "#00AA00", "sighed": "#00AA00", "visited": "#00AA00",
    "chuckled": "#00AA00", "threw": "#00AA00", "dropped": "#00AA00", "considered": "#00AA00", "touched": "#00AA00",
    "wondered": "#00AA00", "attacked": "#00AA00", "acted": "#00AA00", "trusted": "#00AA00", "bore": "#00AA00",
    "reached": "#00AA00", "agreed": "#00AA00", "realized": "#00AA00", "cried": "#00AA00", "noticed": "#00AA00",
    "focused": "#00AA00", "shot": "#00AA00", "explained": "#00AA00", "married": "#00AA00", "joined": "#00AA00",
    "rang": "#00AA00", "taught": "#00AA00", "tasted": "#00AA00", "pushed": "#00AA00", "applied": "#00AA00",
    "drew": "#00AA00", "increased": "#00AA00", "hated": "#00AA00", "grunted": "#00AA00", "searched": "#00AA00",
    "hung": "#00AA00", "protected": "#00AA00", "released": "#00AA00", "prepared": "#00AA00", "charged": "#00AA00",
    "flew": "#00AA00", "cheered": "#00AA00", "required": "#00AA00", "entered": "#00AA00", "danced": "#00AA00",
    "hid": "#00AA00", "removed": "#00AA00", "carried": "#00AA00", "mentioned": "#00AA00", "appeared": "#00AA00",
    "beat": "#00AA00", "filled": "#00AA00", "screamed": "#00AA00", "pressed": "#00AA00", "traveled": "#00AA00",
    "connected": "#00AA00", "accepted": "#00AA00", "fixed": "#00AA00", "served": "#00AA00", "cooked": "#00AA00",
    "woke": "#00AA00", "raised": "#00AA00", "jumped": "#00AA00", "rode": "#00AA00", "imagined": "#00AA00",
    "treated": "#00AA00", "selected": "#00AA00", "recommended": "#00AA00", "subscribed": "#00AA00", "gasped": "#00AA00",
    "arrived": "#00AA00", "rolled": "#00AA00", "smelled": "#00AA00", "surprised": "#00AA00", "handled": "#00AA00",
    "managed": "#00AA00", "developed": "#00AA00", "remained": "#00AA00",

    # Verbos en progresivo (verde #00AA00)
    "being": "#00AA00", "doing": "#00AA00", "having": "#00AA00", "going": "#00AA00", "getting": "#00AA00",
    "liking": "#00AA00", "knowing": "#00AA00", "wanting": "#00AA00", "thinking": "#00AA00", "saying": "#00AA00",
    "seeing": "#00AA00", "making": "#00AA00", "coming": "#00AA00", "looking": "#00AA00", "letting": "#00AA00",
    "taking": "#00AA00", "using": "#00AA00", "needing": "#00AA00", "telling": "#00AA00", "working": "#00AA00",
    "giving": "#00AA00", "finding": "#00AA00", "meaning": "#00AA00", "loving": "#00AA00", "trying": "#00AA00",
    "feeling": "#00AA00", "calling": "#00AA00", "talking": "#00AA00", "helping": "#00AA00", "starting": "#00AA00",
    "leaving": "#00AA00", "putting": "#00AA00", "showing": "#00AA00", "happening": "#00AA00", "keeping": "#00AA00",
    "playing": "#00AA00", "asking": "#00AA00", "waiting": "#00AA00", "changing": "#00AA00", "stopping": "#00AA00",
    "hearing": "#00AA00", "moving": "#00AA00", "eating": "#00AA00", "living": "#00AA00", "turning": "#00AA00",
    "running": "#00AA00", "bringing": "#00AA00", "watching": "#00AA00", "opening": "#00AA00", "laughing": "#00AA00",
    "staying": "#00AA00", "becoming": "#00AA00", "believing": "#00AA00", "setting": "#00AA00", "understanding": "#00AA00",
    "buying": "#00AA00", "meeting": "#00AA00", "holding": "#00AA00", "caring": "#00AA00", "killing": "#00AA00",
    "remembering": "#00AA00", "hoping": "#00AA00", "adding": "#00AA00", "losing": "#00AA00", "learning": "#00AA00",
    "writing": "#00AA00", "checking": "#00AA00", "seeming": "#00AA00", "creating": "#00AA00", "reading": "#00AA00",
    "causing": "#00AA00", "following": "#00AA00", "speaking": "#00AA00", "paying": "#00AA00", "closing": "#00AA00",
    "sending": "#00AA00", "breaking": "#00AA00", "dying": "#00AA00", "winning": "#00AA00", "hitting": "#00AA00",
    "including": "#00AA00", "forgetting": "#00AA00", "sitting": "#00AA00", "walking": "#00AA00", "listening": "#00AA00",
    "falling": "#00AA00", "clicking": "#00AA00", "saving": "#00AA00", "continuing": "#00AA00", "sharing": "#00AA00",
    "fighting": "#00AA00", "cutting": "#00AA00", "drinking": "#00AA00", "posting": "#00AA00", "guessing": "#00AA00",
    "building": "#00AA00", "standing": "#00AA00", "growing": "#00AA00", "providing": "#00AA00", "supporting": "#00AA00",
    "allowing": "#00AA00", "wearing": "#00AA00", "worrying": "#00AA00", "picking": "#00AA00", "choosing": "#00AA00",
    "dealing": "#00AA00", "sleeping": "#00AA00", "driving": "#00AA00", "controlling": "#00AA00", "enjoying": "#00AA00",
    "finishing": "#00AA00", "offering": "#00AA00", "missing": "#00AA00", "leading": "#00AA00", "deciding": "#00AA00",
    "passing": "#00AA00", "selling": "#00AA00", "beginning": "#00AA00", "spending": "#00AA00", "catching": "#00AA00",
    "returning": "#00AA00", "sorting": "#00AA00", "lying": "#00AA00", "designing": "#00AA00", "wishing": "#00AA00",
    "covering": "#00AA00", "pulling": "#00AA00", "hurting": "#00AA00", "studying": "#00AA00", "expecting": "#00AA00",
    "receiving": "#00AA00", "supposing": "#00AA00", "sighing": "#00AA00", "visiting": "#00AA00", "chuckling": "#00AA00",
    "throwing": "#00AA00", "dropping": "#00AA00", "considering": "#00AA00", "touching": "#00AA00", "wondering": "#00AA00",
    "attacking": "#00AA00", "acting": "#00AA00", "trusting": "#00AA00", "bearing": "#00AA00", "reaching": "#00AA00",
    "agreeing": "#00AA00", "realizing": "#00AA00", "crying": "#00AA00", "noticing": "#00AA00", "focusing": "#00AA00",
    "shooting": "#00AA00", "explaining": "#00AA00", "marrying": "#00AA00", "joining": "#00AA00", "ringing": "#00AA00",
    "teaching": "#00AA00", "tasting": "#00AA00", "pushing": "#00AA00", "applying": "#00AA00", "drawing": "#00AA00",
    "increasing": "#00AA00", "hating": "#00AA00", "grunting": "#00AA00", "searching": "#00AA00", "hanging": "#00AA00",
    "protecting": "#00AA00", "releasing": "#00AA00", "preparing": "#00AA00", "charging": "#00AA00", "flying": "#00AA00",
    "cheering": "#00AA00", "requiring": "#00AA00", "entering": "#00AA00", "dancing": "#00AA00", "hiding": "#00AA00",
    "removing": "#00AA00", "carrying": "#00AA00", "mentioning": "#00AA00", "appearing": "#00AA00", "beating": "#00AA00",
    "filling": "#00AA00", "screaming": "#00AA00", "pressing": "#00AA00", "traveling": "#00AA00", "connecting": "#00AA00",
    "accepting": "#00AA00", "fitting": "#00AA00", "fixing": "#00AA00", "serving": "#00AA00", "cooking": "#00AA00",
    "waking": "#00AA00", "raising": "#00AA00", "jumping": "#00AA00", "shutting": "#00AA00", "riding": "#00AA00",
    "imagining": "#00AA00", "treating": "#00AA00", "selecting": "#00AA00", "recommending": "#00AA00", "subscribing": "#00AA00",
    "gasping": "#00AA00", "arriving": "#00AA00", "rolling": "#00AA00", "smelling": "#00AA00", "surprising": "#00AA00",
    "handling": "#00AA00", "managing": "#00AA00", "developing": "#00AA00", "remaining": "#00AA00",

    # Pronombres (rojo)
    "I": "red", "you": "red", "it": "red", "that": "red", "we": "red",
    "this": "red", "he": "red", "they": "red", "what": "red", "my": "red",
    "she": "red", "all": "red", "who": "red", "some": "red", "these": "red",
    "which": "red", "something": "red", "any": "red", "those": "red", "many": "red",
    "most": "red", "everything": "red", "every": "red", "anything": "red", "another": "red",
    "both": "red", "nothing": "red", "each": "red", "someone": "red", "everyone": "red",
    "its": "red", "few": "red", "yourself": "red", "myself": "red", "anyone": "red",
    "whatever": "red", "everybody": "red", "one": "red", "mine": "red", "himself": "red",
    "somebody": "red", "self": "red", "nobody": "red",
    
    # Sustantivos (morado)
    "time": "purple", "thing": "purple", "people": "purple", "way": "purple", "day": "purple",
    "year": "purple", "man": "purple", "lot": "purple", "guy": "purple", "life": "purple",
    "place": "purple", "kind": "purple", "video": "purple", "bit": "purple", "home": "purple",
    "friend": "purple", "end": "purple", "name": "purple", "world": "purple", "part": "purple",
    "point": "purple", "hand": "purple", "money": "purple", "course": "purple", "music": "purple",
    "game": "purple", "woman": "purple", "number": "purple", "girl": "purple", "question": "purple",
    "family": "purple", "house": "purple", "night": "purple", "problem": "purple", "side": "purple",
    "person": "purple", "car": "purple", "water": "purple", "case": "purple", "head": "purple",
    "child": "purple", "kid": "purple", "face": "purple", "job": "purple", "idea": "purple",
    "word": "purple", "mom": "purple", "minute": "purple", "order": "purple", "room": "purple",
    "top": "purple", "week": "purple", "plan": "purple", "school": "purple", "sound": "purple",
    "dad": "purple", "mind": "purple", "line": "purple", "eye": "purple", "team": "purple",
    "information": "purple", "power": "purple", "business": "purple", "body": "purple", "hour": "purple",
    "book": "purple", "month": "purple", "phone": "purple", "door": "purple", "food": "purple",
    "story": "purple", "company": "purple", "light": "purple", "matter": "purple", "experience": "purple",
    "reason": "purple", "service": "purple", "mother": "purple", "heart": "purple", "answer": "purple",
    "fun": "purple", "system": "purple", "stuff": "purple", "color": "purple", "father": "purple",
    "baby": "purple", "boy": "purple", "product": "purple", "example": "purple", "country": "purple",
    "type": "purple", "fact": "purple", "moment": "purple", "step": "purple", "base": "purple",
    "website": "purple", "area": "purple", "brother": "purple", "son": "purple", "morning": "purple",
    "level": "purple", "party": "purple", "cookie": "purple", "data": "purple", "front": "purple",
    "group": "purple", "comment": "purple", "half": "purple", "piece": "purple", "test": "purple",
    "song": "purple", "state": "purple", "process": "purple", "rest": "purple", "sir": "purple",
    "term": "purple", "dog": "purple", "user": "purple", "fire": "purple", "store": "purple",
    "hair": "purple", "student": "purple", "form": "purple", "chance": "purple", "result": "purple",
    "couple": "purple", "human": "purple", "picture": "purple", "list": "purple", "price": "purple",
    "sign": "purple", "space": "purple", "issue": "purple", "class": "purple", "city": "purple",
    "link": "purple", "value": "purple", "future": "purple", "dream": "purple", "date": "purple",
    "past": "purple", "report": "purple", "site": "purple", "foot": "purple", "wife": "purple",
    "law": "purple", "project": "purple", "shit": "purple", "sense": "purple", "member": "purple",
    "force": "purple", "key": "purple", "card": "purple", "movie": "purple", "figure": "purple",
    "parent": "purple", "box": "purple", "option": "purple", "page": "purple", "news": "purple",
    "camera": "purple", "record": "purple", "death": "purple", "police": "purple", "daughter": "purple",
    "board": "purple", "hell": "purple", "situation": "purple", "cost": "purple", "program": "purple",
    "view": "purple", "promise": "purple", "sister": "purple", "market": "purple", "voice": "purple",
    "size": "purple", "event": "purple", "note": "purple", "film": "purple", "channel": "purple",
    "position": "purple", "air": "purple", "feature": "purple", "contact": "purple", "rule": "purple",
    "truth": "purple", "relationship": "purple", "tonight": "purple", "practice": "purple", "doctor": "purple",
    "file": "purple", "image": "purple", "ball": "purple", "character": "purple", "energy": "purple",
    "star": "purple", "message": "purple", "language": "purple", "content": "purple", "email": "purple",
    "model": "purple", "excuse": "purple", "office": "purple", "account": "purple", "customer": "purple",
    "amount": "purple", "window": "purple", "feeling": "purple", "shot": "purple", "photo": "purple",
    "table": "purple", "lady": "purple", "player": "purple", "blood": "purple", "choice": "purple",
    "difference": "purple", "access": "purple", "action": "purple", "train": "purple", "quality": "purple",
    "detail": "purple", "fan": "purple", "community": "purple", "trouble": "purple", "narrator": "purple",
    "leg": "purple", "age": "purple", "land": "purple", "button": "purple", "stick": "purple",
    "material": "purple", "government": "purple", "middle": "purple", "tree": "purple", "decision": "purple",
    "condition": "purple", "effect": "purple", "bag": "purple", "master": "purple", "health": "purple",
    "machine": "purple", "field": "purple", "address": "purple", "cake": "purple", "wall": "purple",
    "history": "purple", "husband": "purple", "skin": "purple", "challenge": "purple", "track": "purple",
    "audience": "purple", "match": "purple", "arm": "purple", "war": "purple", "pain": "purple",
    "function": "purple", "style": "purple", "bottom": "purple", "bed": "purple", "center": "purple",
    "rate": "purple", "tool": "purple", "rock": "purple", "building": "purple", "secret": "purple",
    "road": "purple", "item": "purple", "gun": "purple", "oil": "purple", "opportunity": "purple",
    "fish": "purple", "code": "purple", "dollar": "purple", "ground": "purple", "cell": "purple",
    "mistake": "purple", "teacher": "purple", "goal": "purple", "version": "purple", "screen": "purple",
    "town": "purple", "tv": "purple", "attention": "purple", "floor": "purple", "scene": "purple",
    "speed": "purple", "performance": "purple", "computer": "purple", "review": "purple", "stage": "purple",
    "dress": "purple", "shape": "purple", "animal": "purple", "dinner": "purple", "paper": "purple",
    "cat": "purple",
    
    # Artículos (azul)
    "the": "blue", "a": "blue", "an": "blue",

    # Conjunciones (marrón #8B4513)
    "and": "#8B4513", "but": "#8B4513", "if": "#8B4513", "or": "#8B4513", "when": "#8B4513",
    "because": "#8B4513", "while": "#8B4513", "though": "#8B4513", "either": "#8B4513", 
    "whether": "#8B4513", "ll": "#8B4513",  # Contracción de "will"

    # Adjetivos (rosado #FFC0CB) - Orden alfabético
    "able": "#FFC0CB", "afraid": "#FFC0CB", "alright": "#FFC0CB", "alone": "#FFC0CB", "amazing": "#FFC0CB",
    "available": "#FFC0CB", "awesome": "#FFC0CB", "bad": "#FFC0CB", "beautiful": "#FFC0CB", "best": "#FFC0CB",
    "better": "#FFC0CB", "big": "#FFC0CB", "black": "#FFC0CB", "cold": "#FFC0CB", "clean": "#FFC0CB",
    "clear": "#FFC0CB", "cool": "#FFC0CB", "complete": "#FFC0CB", "crazy": "#FFC0CB", "cute": "#FFC0CB",
    "certain": "#FFC0CB", "dead": "#FFC0CB", "deep": "#FFC0CB", "different": "#FFC0CB", "difficult": "#FFC0CB",
    "early": "#FFC0CB", "easy": "#FFC0CB", "entire": "#FFC0CB", "even": "#FFC0CB", "excellent": "#FFC0CB",
    "exciting": "#FFC0CB", "favorite": "#FFC0CB", "fine": "#FFC0CB", "first": "#FFC0CB", "free": "#FFC0CB",
    "full": "#FFC0CB", "funny": "#FFC0CB", "good": "#FFC0CB", "great": "#FFC0CB", "green": "#FFC0CB",
    "happy": "#FFC0CB", "hard": "#FFC0CB", "high": "#FFC0CB", "hot": "#FFC0CB", "huge": "#FFC0CB",
    "important": "#FFC0CB", "interesting": "#FFC0CB", "large": "#FFC0CB", "late": "#FFC0CB", "left": "#FFC0CB",
    "little": "#FFC0CB", "local": "#FFC0CB", "long": "#FFC0CB", "longer": "#FFC0CB", "low": "#FFC0CB",
    "main": "#FFC0CB", "new": "#FFC0CB", "nice": "#FFC0CB", "normal": "#FFC0CB", "old": "#FFC0CB",
    "online": "#FFC0CB", "other": "#FFC0CB", "own": "#FFC0CB", "perfect": "#FFC0CB", "personal": "#FFC0CB",
    "possible": "#FFC0CB", "pretty": "#FFC0CB", "public": "#FFC0CB", "quick": "#FFC0CB", "ready": "#FFC0CB",
    "real": "#FFC0CB", "red": "#FFC0CB", "right": "#FFC0CB", "round": "#FFC0CB", "safe": "#FFC0CB",
    "same": "#FFC0CB", "second": "#FFC0CB", "serious": "#FFC0CB", "short": "#FFC0CB", "simple": "#FFC0CB",
    "single": "#FFC0CB", "small": "#FFC0CB", "social": "#FFC0CB", "special": "#FFC0CB", "straight": "#FFC0CB",
    "strong": "#FFC0CB", "such": "#FFC0CB", "super": "#FFC0CB", "sure": "#FFC0CB", "sweet": "#FFC0CB",
    "third": "#FFC0CB", "true": "#FFC0CB", "weird": "#FFC0CB", "white": "#FFC0CB", "whole": "#FFC0CB",
    "worth": "#FFC0CB", "wrong": "#FFC0CB", "young": "#FFC0CB",

    # Adverbios (naranja #FFA500) - Orden alfabético
    "absolutely": "#FFA500", "actually": "#FFA500", "again": "#FFA500", "ago": "#FFA500", "ahead": "#FFA500",
    "almost": "#FFA500", "already": "#FFA500", "also": "#FFA500", "always": "#FFA500", "anyway": "#FFA500",
    "away": "#FFA500", "back": "#FFA500", "basically": "#FFA500", "completely": "#FFA500", "definitely": "#FFA500",
    "down": "#FFA500", "else": "#FFA500", "enough": "#FFA500", "even": "#FFA500", "ever": "#FFA500",
    "exactly": "#FFA500", "far": "#FFA500", "fast": "#FFA500", "finally": "#FFA500", "forward": "#FFA500",
    "here": "#FFA500", "how": "#FFA500", "however": "#FFA500", "just": "#FFA500", "later": "#FFA500",
    "least": "#FFA500", "less": "#FFA500", "more": "#FFA500", "much": "#FFA500", "never": "#FFA500",
    "no": "#FFA500", "not": "#FFA500", "now": "#FFA500", "often": "#FFA500", "only": "#FFA500",
    "out": "#FFA500", "probably": "#FFA500", "quite": "#FFA500", "really": "#FFA500", "simply": "#FFA500",
    "so": "#FFA500", "sometimes": "#FFA500", "soon": "#FFA500", "still": "#FFA500", "there": "#FFA500",
    "then": "#FFA500", "today": "#FFA500", "together": "#FFA500", "too": "#FFA500", "up": "#FFA500",
    "very": "#FFA500", "well": "#FFA500", "where": "#FFA500", "why": "#FFA500", "yet": "#FFA500",

    # Preposiciones (amarillo #FFFF00) - Orden alfabético
    "about": "#FFFF00", "above": "#FFFF00", "across": "#FFFF00", "after": "#FFFF00", "against": "#FFFF00",
    "along": "#FFFF00", "around": "#FFFF00", "as": "#FFFF00", "at": "#FFFF00", "before": "#FFFF00",
    "behind": "#FFFF00", "below": "#FFFF00", "between": "#FFFF00", "by": "#FFFF00", "during": "#FFFF00",
    "for": "#FFFF00", "from": "#FFFF00", "in": "#FFFF00", "inside": "#FFFF00", "into": "#FFFF00",
    "of": "#FFFF00", "off": "#FFFF00", "on": "#FFFF00", "out": "#FFFF00", "over": "#FFFF00",
    "per": "#FFFF00", "plus": "#FFFF00", "since": "#FFFF00", "through": "#FFFF00", "to": "#FFFF00",
    "under": "#FFFF00", "until": "#FFFF00", "with": "#FFFF00", "within": "#FFFF00", "without": "#FFFF00"}

# ====================== FUNCIONES DE GESTIÓN DE DATOS ======================
@st.cache_data
def cargar_palabras_colores():
    try:
        if os.path.exists(PALABRAS_COLORES_JSON) and os.path.getsize(PALABRAS_COLORES_JSON) > 0:
            with open(PALABRAS_COLORES_JSON, "r", encoding="utf-8") as f:
                return {**palabras_base, **json.load(f)}
        return palabras_base.copy()
    except Exception:
        return palabras_base.copy()

palabras_colores = cargar_palabras_colores()

def guardar_palabras_colores():
    try:
        with open(PALABRAS_COLORES_JSON, "w", encoding="utf-8") as f:
            json.dump(palabras_colores, f, indent=4)
        st.success("Diccionario guardado correctamente")
    except Exception as e:
        st.error(f"No se pudo guardar: {str(e)}")

# ====================== FUNCIONES DE PROCESAMIENTO ======================
@lru_cache(maxsize=1000)
def obtener_color(palabra):
    return palabras_colores.get(palabra.lower())

def limpiar_texto(texto):
    return "\n".join([re.sub(r'\s+', ' ', linea).strip() for linea in texto.splitlines()])

def aplicar_colores_html(texto):
    lineas = texto.split('\n')
    resultado = []
    for linea in lineas:
        if not linea.strip():
            resultado.append('<br>')
            continue
        
        # Procesar cada línea manteniendo el formato original
        linea_procesada = []
        for segmento in re.findall(r"([a-zA-Z']+|\W+)", linea):  # Regex mejorado
            if segmento.strip():
                palabra_limpia = segmento.lower().strip(".,!?;:\"'")
                color = obtener_color(palabra_limpia)
                if color:
                    linea_procesada.append(
                        f'<span style="color: black; border-bottom: 2px solid {color}">{segmento}</span>'
                    )
                else:
                    linea_procesada.append(segmento)
            else:
                linea_procesada.append(segmento)
        
        resultado.append(''.join(linea_procesada))
    return '<br>'.join(resultado)

# ====================== FUNCIONES PARA ARCHIVOS ======================
def procesar_archivo(uploaded_file):
    try:
        if uploaded_file.name.endswith('.pdf'):
            with pdfplumber.open(uploaded_file) as pdf:
                return "\n".join([pagina.extract_text() or "" for pagina in pdf.pages if pagina.extract_text()])
        else:
            return uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error al procesar archivo: {str(e)}")
        return ""

# ====================== FUNCIONES PARA YOUTUBE ======================
def descargar_subtitulos_youtube(url):
    try:
        video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url).group(1)
        subtitles = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB', 'a.en'])
        return "\n".join([line['text'] for line in subtitles])
    except Exception as e:
        st.error(f"No se pudieron obtener subtítulos: {str(e)}")
        return ""

# ====================== CHAT CON IA ======================
class ChatAI:
    def __init__(self):
        self.idioma_respuesta = "ambos"
        self.base_url = "http://localhost:11434/api/generate"
        self.model = "llama3"

    def generar_respuesta(self, mensaje):
        try:
            prompt = mensaje
            if self.idioma_respuesta == "español":
                prompt += " (responde en español)"
            elif self.idioma_respuesta == "ambos":
                prompt += " (responde primero en inglés, luego en español)"
                
            response = requests.post(
                self.base_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            return response.json()["response"]
        except Exception as e:
            return f"Error: {str(e)}"

# ====================== INTERFAZ STREAMLIT ======================
def main():
    
    # CSS personalizado
    st.markdown("""
    <style>
        .texto-coloreado {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            white-space: pre-wrap;
            color: black !important;  /* Fuerza texto negro */
            font-size: 16px;
            line-height: 1.8;
        }
        .texto-coloreado span {
            color: black !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar para configuración
    with st.sidebar:
        st.title("⚙️ Configuración")
        
        # Gestión del diccionario
        st.subheader("Diccionario de palabras")
        nueva_palabra = st.text_input("Nueva palabra")
        nueva_categoria = st.selectbox("Categoría", list(CATEGORIAS.keys()))
        
        if st.button("Agregar palabra"):
            if nueva_palabra and nueva_categoria:
                palabras_colores[nueva_palabra.lower()] = CATEGORIAS[nueva_categoria]
                guardar_palabras_colores()
                st.rerun()
        
        # Estadísticas
        st.subheader("📊 Estadísticas")
        for cat, color in CATEGORIAS.items():
            count = sum(1 for word, col in palabras_colores.items() if col.lower() == color.lower())
            st.markdown(f"<span style='color:{color}'>{cat.capitalize()}: {count}</span>", unsafe_allow_html=True)
        
        if st.button("Guardar diccionario"):
            guardar_palabras_colores()
    
    # Contenido principal
    st.title("🎨 Language Colorizer Pro")
    
    # Pestañas para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["Editor de Texto", "Chat con IA", "Configuración Avanzada"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cargar contenido")
            opcion = st.radio("Fuente:", ("Texto manual", "Archivo", "YouTube"))
            
            texto = ""
            if opcion == "Texto manual":
                texto = st.text_area("Escribe o pega tu texto aquí:", height=300)
            elif opcion == "Archivo":
                uploaded_file = st.file_uploader("Sube un archivo (TXT o PDF)", type=["txt", "pdf"])
                if uploaded_file:
                    texto = procesar_archivo(uploaded_file)
            elif opcion == "YouTube":
                url = st.text_input("URL de YouTube:")
                if url:
                    texto = descargar_subtitulos_youtube(url)
            
            if st.button("Procesar texto"):
                if texto:
                    st.session_state.texto_procesado = limpiar_texto(texto)
                else:
                    st.warning("Ingresa algún texto primero")
        
        with col2:
            st.subheader("Resultado coloreado")
            if "texto_procesado" in st.session_state:
                html_content = aplicar_colores_html(st.session_state.texto_procesado)
                st.markdown(f'<div class="texto-coloreado">{html_content}</div>', unsafe_allow_html=True)
                
                # Exportar a HTML
                html_full = f"""<!DOCTYPE html>
    <html>
<head>
    <meta charset="UTF-8">
    <title>Documento Exportado</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
        .contenido {{ background-color: white; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="contenido">{html_content}</div>
</body>
</html>"""
                
                st.download_button(
                    label="Descargar como HTML",
                    data=html_full,
                    file_name="texto_coloreado.html",
                    mime="text/html"
                )
            else:
                st.info("Procesa algún texto para ver el resultado aquí")
    
    with tab2:
        st.subheader("💬 Chat Bilingüe con IA")
        
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
        
        # Mostrar historial de chat
        for msg in st.session_state.chat_messages:
            role = "user" if msg["role"] == "user" else "assistant"
            color = "#1a73e8" if role == "user" else "#0b8043"
            st.markdown(f"<span style='color:{color}; font-weight:bold'>{'Tú' if role == 'user' else 'IA'}:</span> {msg['content']}", unsafe_allow_html=True)
        
        # Configuración del chat
        idioma = st.radio("Idioma de respuesta:", ["Ambos", "Inglés", "Español"], horizontal=True)
        
        # Entrada de mensaje
        user_input = st.text_area("Escribe tu mensaje:", key="chat_input")
        
        if st.button("Enviar") and user_input:
            chatbot = ChatAI()
            chatbot.idioma_respuesta = idioma.lower()
            
            # Agregar mensaje del usuario
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            # Obtener respuesta
            respuesta = chatbot.generar_respuesta(user_input)
            
            # Agregar respuesta de la IA
            st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})
            
            # Rerun para actualizar la vista
            st.rerun()
    
    with tab3:
        st.subheader("Configuración avanzada del diccionario")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_busqueda = st.text_input("Buscar palabra:")
        with col2:
            filtro_categoria = st.selectbox("Filtrar por categoría", ["Todas"] + list(CATEGORIAS.keys()))
        
        # Mostrar palabras del diccionario
        palabras_filtradas = []
        for palabra, color in palabras_colores.items():
            categoria = obtener_categoria_por_color(color)
            if (filtro_categoria == "Todas" or categoria == filtro_categoria) and \
               (not filtro_busqueda or filtro_busqueda.lower() in palabra.lower()):
                palabras_filtradas.append((palabra, categoria, color))
        
        # Tabla de palabras
        if palabras_filtradas:
            for palabra, categoria, color in sorted(palabras_filtradas, key=lambda x: x[0].lower()):
                cols = st.columns([4, 3, 2, 1])
                cols[0].markdown(f"**{palabra}**")
                cols[1].markdown(f"<span style='color:{color}'>{categoria}</span>", unsafe_allow_html=True)
                cols[2].markdown(f"`{color}`")
                if cols[3].button("❌", key=f"del_{palabra}"):
                    del palabras_colores[palabra]
                    guardar_palabras_colores()
                    st.rerun()
        else:
            st.info("No hay palabras que coincidan con los filtros")

def obtener_categoria_por_color(color):
    for cat, col in CATEGORIAS.items():
        if col.lower() == color.lower():
            return cat
    return "Desconocida"

if __name__ == "__main__":
    main()