import re
from utils import config

class TextProcessor: 

    PATTERNS = {
        'emoji': re.compile(
            "(["
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002600-\U00002B55"
            "\U0000FE0E-\U0000FE0F"
            "])",
            flags=re.UNICODE,
        )
        'url': re.compile(r'https?://\S+|www\.\S+|t\.me/\S+|tg://\S+'),
        'mention': re.compile(r'[@#]\w+'), 
        'quotes': re.compile(r'[«»"`´]'),
        'source': re.compile(r',?\s*(пишет|сообщает|по данным|источник|сообщают|сообщили)\s+[^.!?]+(?=[.!?]|$)', re.IGNORECASE),
        'spaces': re.compile(r'\s+'),
        'multi_excl': re.compile(r'!{3,}'),
        'multi_quest': re.compile(r'\?{3,}')
    }

    def __init__(self, cfg=None):
        config_cfg = config.get("preprocessing", {}).get("text_processor", {})
        self.cfg = cfg or config_cfg
        self.skip_phrases = self.cfg.get('skip_substrings', [])
        self.rm_phrases = sorted(self.cfg.get('rm_substrings', []), key=len, reverse=True)
        self.bad_words = self.cfg.get('obscene_substrings', [])

    def clean(self, text):
        if not text or self._skip(text):
            return ""
        
        text = self._preserve_numeric_ranges(text)
        text = self._rm_phrases(text)

        cleaners = [
            self._rm_emoji,
            self._rm_links,
            self._norm_quotes,
            self._norm_punct,
            self.remove_soucres,
            self._clean_paras,
            self._norm_spaces,
            self._keep_symbols
        ]
        
        for cleaner in cleaners:
            text = cleaner(text)
            if not text:
                return ""
        
        return text if len(text.strip()) >= 5 else ""
        
    def _preserve_numeric_ranges(self, text):

        def fix_decimal(match):
            n1 = match.group(1).replace(',', '.')  
            n2 = match.group(2).replace(',', '.')
            return f"{n1}-{n2}"

        def fix_simple(match):
            return f"{match.group(1)}-{match.group(2)}"

        text = re.sub(r'(\d+[,\.]\d+)\s*[–\-]\s*(\d+[,\.]?\d*)', fix_decimal, text)
        text = re.sub(r'(\d+)\s*[–\-]\s*(\d+)', fix_simple, text)
        return text

    def _skip(self, text):
        lower_text = text.lower()
        return any(phrase.lower() in lower_text for phrase in self.skip_phrases)
    
    def _rm_phrases(self, text):
        for phrase in self.rm_phrases:
            text = text.replace(phrase, " ")
        return text
    
    def _norm_punct(self, text):
        text = re.sub(r'\.{3,}|…', '...', text)
        text = self.PATTERNS['multi_excl'].sub('!', text)
        text = self.PATTERNS['multi_quest'].sub('?', text)
        text = re.sub(r'(\d+)\s*(процентов|проц)', r'\1%', text, flags=re.IGNORECASE)
        return text
        
    def _keep_symbols(self, text):
        text = re.sub(r'(\d+)%', r'\1%', text)
        text = re.sub(r'\$(\d+)', r'$\1', text) 
        text = re.sub(r'€(\d+)', r'€\1', text)  
        text = re.sub(r'№\s*(\d+)', r'№\1', text)
        return text

    def _rm_emoji(self, text): 
        return self.PATTERNS['emoji'].sub('', text)
    
    def _rm_links(self, text):
        text = self.PATTERNS['url'].sub('', text)
        text = self.PATTERNS['mention'].sub('', text)
        return text

    def remove_soucres(self, text):
        text = self.PATTERNS['source'].sub('', text)
        text = re.sub(r'\s*,\s*\.', '.', text)  
        text = re.sub(r'\s*,\s*,', ',', text)   
        text = re.sub(r'\s*\.\s*\.', '.', text)
        text = re.sub(r'\s+', ' ', text)        
        text = re.sub(r'\s*,\s*$', '', text)
        return text

    
    def _norm_quotes(self, text):
        text = self.PATTERNS['quotes'].sub('"', text)
        text = re.sub(r'^"+|"+$', '', text)
        if text.count('"') % 2 != 0:
            text = text.replace('"', ' ')
        return text.strip()
    
    def _clean_paras(self, text):
        paras = [
            ' '.join(p.split()).strip() 
            for p in text.split('\n') 
            if len(' '.join(p.split()).strip()) >= 5
        ]
        return '\n'.join(paras)
    
    def _norm_spaces(self, text):
        text = self.PATTERNS['spaces'].sub(' ', text)
        return text.strip()